import ast
import json
import re
import ollama
from config.settings import settings
from config.logging import logger
from agent.mcp_client import MCPClientManager
from agent.prompts import SYSTEM_PROMPT, build_tool_descriptions


class ReActAgent:
    def __init__(self, mcp_manager: MCPClientManager):
        self.mcp_manager = mcp_manager
        self.model = settings.OLLAMA_MODEL
        self.max_iterations = 6

    def _build_system_prompt(self) -> str:
        tools = self.mcp_manager.get_tools_for_llm()
        tool_names = ", ".join(t["name"] for t in tools)
        base = SYSTEM_PROMPT.format(tool_descriptions=build_tool_descriptions(tools))
        base += (
            f"\n\nCRITICAL RULES:\n"
            f"- The ONLY tools that exist are: {tool_names}. There is NO tool for "
            f"comparing skills, ranking jobs, calculating match percentage, or "
            f"finalizing an answer. Those are things YOU must do yourself through "
            f"reasoning, then write directly as the Final Answer JSON.\n"
            f"- If you catch yourself about to call a tool not in this exact list, "
            f"STOP — do the comparison in your own reasoning instead and go straight "
            f"to Final Answer.\n"
            "- Produce ONLY ONE of: (a) a single Thought+Action+Action Input block, "
            "OR (b) a single Thought+Final Answer block. Never both in the same response.\n"
            "- Action Input MUST be valid JSON using DOUBLE QUOTES only.\n"
            "- After writing Action Input, STOP. Do not write anything else.\n"
            "- NEVER invent company names, URLs, or job data. Only use data that appears "
            "in a real Observation message sent back to you by the system."
        )
        return base

    def _call_llm(self, messages: list[dict]) -> str:
        response = ollama.chat(
            model=self.model,
            messages=messages,
            options={"stop": ["Observation:", "\nObservation", "[Assuming"]},
        )
        return response["message"]["content"]

    def _extract_json_block(self, text: str, marker: str):
        idx = text.find(marker)
        if idx == -1:
            return None
        brace_start = text.find("{", idx)
        if brace_start == -1:
            return None
        depth = 0
        for i in range(brace_start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return text[brace_start:i + 1]
        return None

    def _safe_parse_dict(self, raw: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        try:
            parsed = ast.literal_eval(raw)
            if isinstance(parsed, dict):
                return parsed
        except (ValueError, SyntaxError):
            pass
        logger.info(f"Failed to parse tool input, raw text was: {raw}")
        return {}

    async def run(self, user_request: str) -> dict:
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": user_request},
        ]
        valid_tool_names = {t["name"] for t in self.mcp_manager.get_tools_for_llm()}
        have_resume = False
        have_jobs = False

        for step in range(self.max_iterations):
            # Once both real observations are in, don't even let the model try another
            # Action — force it straight to Final Answer.
            if have_resume and have_jobs:
                messages.append({
                    "role": "user",
                    "content": (
                        "You now have both the resume skills and the job listings above. "
                        "Do NOT call any more tools — none exist for comparison or ranking. "
                        "Reason it out yourself and respond with ONLY a Final Answer JSON block now."
                    )
                })

            llm_output = self._call_llm(messages)
            logger.info(f"[Step {step}] LLM output:\n{llm_output}")

            final_idx = llm_output.find("Final Answer:")
            action_idx = llm_output.find("Action:")

            if final_idx != -1 and (action_idx == -1 or final_idx < action_idx):
                json_str = self._extract_json_block(llm_output, "Final Answer:")
                if json_str:
                    parsed = self._safe_parse_dict(json_str)
                    if parsed:
                        return parsed
                return {"error": "Model returned a malformed Final Answer. Try again."}

            if action_idx != -1:
                action_segment = llm_output[action_idx:]
                tool_match = re.search(r"Action:\s*(\w+)", action_segment)
                json_str = self._extract_json_block(action_segment, "Action Input:")

                if not tool_match or not json_str:
                    messages.append({"role": "assistant", "content": llm_output[:action_idx + 200]})
                    messages.append({
                        "role": "user",
                        "content": "Invalid Action format. Use exactly: Action: <tool_name> then Action Input: <valid JSON>."
                    })
                    continue

                tool_name = tool_match.group(1).strip()

                # Catch hallucinated tools immediately with a clear correction,
                # instead of wasting a full round-trip on a doomed tool call.
                if tool_name not in valid_tool_names:
                    messages.append({"role": "assistant", "content": llm_output[:action_idx] + f"Action: {tool_name}"})
                    messages.append({
                        "role": "user",
                        "content": (
                            f"'{tool_name}' is not a real tool. The only tools available are: "
                            f"{', '.join(valid_tool_names)}. If you already have both resume "
                            f"skills and job listings, do the comparison yourself and write a "
                            f"Final Answer now instead of calling a tool."
                        )
                    })
                    continue

                tool_input = self._safe_parse_dict(json_str)
                if not tool_input:
                    messages.append({"role": "assistant", "content": llm_output[:action_idx] + f"Action: {tool_name}\nAction Input: {json_str}"})
                    messages.append({
                        "role": "user",
                        "content": f"Your Action Input '{json_str}' could not be parsed. Rewrite as valid double-quoted JSON."
                    })
                    continue

                server_name = next(
                    (t["server"] for t in self.mcp_manager.available_tools if t["name"] == tool_name),
                    None
                )
                try:
                    result = await self.mcp_manager.call_tool(server_name, tool_name, tool_input)
                    observation = str(result.content)
                    if tool_name == "analyze_resume":
                        have_resume = True
                    elif tool_name == "search_jobs":
                        have_jobs = True
                except Exception as e:
                    observation = f"Error calling tool: {e}"

                logger.info(f"[Step {step}] Tool called: {tool_name}({tool_input})\nObservation: {observation}")

                clean_segment = llm_output[:action_idx] + f"Action: {tool_name}\nAction Input: {json_str}"
                messages.append({"role": "assistant", "content": clean_segment})
                messages.append({"role": "user", "content": f"Observation: {observation}"})
                continue

            messages.append({"role": "assistant", "content": llm_output})
            messages.append({
                "role": "user",
                "content": "You must respond with either an Action or a Final Answer in the correct format."
            })

        return {"error": "The agent couldn't complete the task in time. Try a more specific job role or check your resume PDF is readable."}
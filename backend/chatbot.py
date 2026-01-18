import os
import google.generativeai as genai
from flask import jsonify
import config
import tools
from datetime import datetime

from google.generativeai.types import HarmCategory, HarmBlockThreshold

class WeddingChatbot:
    def __init__(self):
        api_key = config.GEMINI_API_KEY
        if not api_key:
            self.model = None
            self.sessions = {}
        else:
            genai.configure(api_key=api_key)
            self.agent_tools = [
                tools.check_wedding_hall_availability, 
                tools.get_available_slots,
                tools.book_tour, 
                tools.book_manager_meeting,
                tools.search_venue_knowledge
            ]
            
            # Reduce safety filters to avoid false positives in a demo environment
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            self.model = genai.GenerativeModel(
                config.GENERATION_MODEL_NAME, 
                tools=self.agent_tools,
                system_instruction=self._get_system_instruction(),
                safety_settings=safety_settings
            )
            self.sessions = {}
            try:
                tools.get_cal_me()
            except Exception as e:
                print(f"Warning: Calendar init failed: {e}")

    def _get_system_instruction(self):
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        return config.CHATBOT_SYSTEM_INSTRUCTION + f"\n\nCRITICAL: Today is {current_date}. Keep this in mind."

    def _summarize_history(self, history):
        """Summarizes chat history, preserving key details like names and dates."""
        if not history: return ""
        summary_model = genai.GenerativeModel(config.GENERATION_MODEL_NAME)
        
        history_text = ""
        for turn in history:
            role = "User" if turn.role == "user" else "Assistant"
            for part in turn.parts:
                if hasattr(part, 'text') and part.text:
                    history_text += f"{role}: {part.text}\n"
                elif hasattr(part, 'function_call'):
                    history_text += f"{role}: [Tool Call: {part.function_call.name}]\n"
                elif hasattr(part, 'function_response'):
                    history_text += f"System: [Tool Result: {part.function_response.name}]\n"
        
        prompt = f"Summarize this wedding venue inquiry conversation concisely. MANDATORY: You MUST preserve the user's name, their email, the specific date they asked for, and the time they selected. These are the most important details. History:\n\n{history_text}"
        
        try:
            response = summary_model.generate_content(prompt)
            return response.text
        except:
            return "Ongoing discussion about wedding booking."

    def get_response(self, user_message, session_id):
        print(f"\n{'='*40}\n[USER] {user_message}\n{'='*40}")
        if not self.model: return {"text": "Brain offline.", "thoughts": "No API Key.", "tools": []}
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'chat': self.model.start_chat(history=[], enable_automatic_function_calling=True),
                'summary': ""
            }
        
        session = self.sessions[session_id]
        
        try:
            # Memory Management: Sliding window based on turn count
            # Gemini history turns are usually pairs, but tools add more parts.
            # We treat the limit as "total message parts" for simplicity, but more robust.
            limit = getattr(config, 'CHAT_HISTORY_LIMIT', 10)
            if len(session['chat'].history) > limit:
                # Keep the last few turns (User-Model exchange)
                to_summarize = session['chat'].history[:-limit]
                keep_recent = session['chat'].history[-limit:]
                
                # Ensure we don't slice middle of a tool call
                # Slicing should ideally happen BEFORE a user message
                while keep_recent and keep_recent[0].role != 'user':
                    to_summarize.append(keep_recent.pop(0))

                new_summary = self._summarize_history(to_summarize)
                session['summary'] = f"PREVIOUS SUMMARY: {new_summary}"
                
                # Start fresh with system context + summary
                new_history = [{'role': 'user', 'parts': [{'text': session['summary']}]}, 
                               {'role': 'model', 'parts': [{'text': "Understood. I have preserved the details of our previous discussion."}]}]
                
                # Append recent history (convert to dict format for start_chat)
                for h in keep_recent:
                    new_history.append({'role': h.role, 'parts': h.parts})
                
                session['chat'] = self.model.start_chat(history=new_history, enable_automatic_function_calling=True)

            context_prefix = ""
            if len(session['chat'].history) == 0:
                 context_prefix = f"[Context: Today is {datetime.now().strftime('%A, %B %d, %Y')}] "

            # Get response
            response = session['chat'].send_message(context_prefix + user_message)
            
            # Check if response is valid/readable
            try:
                 # Attempt to access text to verify valid response parts
                 text_check = response.text
            except ValueError:
                 print(f"!! Safety Block Triggered: {response.prompt_feedback}")
                 return {
                     "text": "I apologize, but I cannot fulfill that request due to safety guidelines.",
                     "thoughts": "Response blocked by safety filters.",
                     "tools": [],
                     "usage": {"input": 0, "output": 0, "total": 0} 
                 }
            
            # Extract tools used
            tools_used = []
            for turn in session['chat'].history[-4:]:
                for part in turn.parts:
                    fn = getattr(part, 'function_call', None)
                    if fn: tools_used.append(fn.name)

            # Token Usage
            usage = getattr(response, 'usage_metadata', None)
            t_in = usage.prompt_token_count if usage else 0
            t_out = usage.candidates_token_count if usage else 0
            t_tot = usage.total_token_count if usage else 0

            thought_preview = response.text[:100].replace('\n', ' ')
            
            # EXACT LOGGING FORMAT REQUESTED BY USER
            print(f"user input-{user_message}")
            print(f"tools use-{', '.join(set(tools_used)) if tools_used else 'None'}")
            print(f"agent thogth(internal thinking)-{thought_preview}...")
            print(f"tokens used-{t_in}, {t_out}, {t_tot}")
            print(f"agent replay-{response.text[:150].strip()}...\n")

            return {
                "text": response.text,
                "thoughts": f"Used tools: {', '.join(tools_used)}" if tools_used else "Direct answer",
                "tools": tools_used,
                "usage": {"input": t_in, "output": t_out, "total": t_tot}
            }
            
        except Exception as e:
            print(f"!! Chat Error: {e}")
            return {"text": "I apologize, I'm having trouble connecting.", "thoughts": str(e), "tools": []}

import os
import requests
import webbrowser

def main():
    userinput = "" 
    print("System Online. Type 'exit' to quit.")

    while userinput.lower() != "exit":
        userinput = input("\nEnter Command: ")
        
        if userinput.lower() == "exit":
            break

        # 1. READ STUDENT DATA (Safe Mode)
        file_content = ""
        try:
            with open("student_data.txt", "r") as file:
                file_content = file.read()
        except FileNotFoundError:
            pass

        # 2. CONSTRUCT THE PROMPT
        payload = {
            "model": "llama3.1",
            "stream": False,
            "system": f"""
            You are an automation assistant. 
            
            [DATA CONTEXT]
            {file_content}
            
            [RULES]
            1. [InFile]: If asking about the student data. Format: [InFile]: <answer>
            2. [APP]: If opening a tool (Notepad, Calc). Format: [APP]: <app_name>
            3. [WEB]: If opening a website (YouTube, Google). Format: [WEB]: <url>
            4. [WRITE]: If user asks to "write about X in notepad". Format: [WRITE]: <content>
            5. [HELP]: If user asks for code help/debugging. Format: [HELP]: <solution_and_explanation>
            
            Output NOTHING else.
            """,
            "prompt": f"Command: {userinput}"
        }
        
        result = ai_response(payload)
        print(result)

def ai_response(payload):
    print("AI is thinking...")
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        action = response.json()['response'].strip()
        
        # print(f"DEBUG: AI Decision -> {action}")

        # 3. ROUTER LOGIC
        if action.startswith("[APP]:"):
            app_name = action.replace("[APP]:", "").strip()
            os.system(f"start {app_name}")
            return f"✅ Opened {app_name}"

        elif action.startswith("[WEB]:"):
            url = action.replace("[WEB]:", "").strip()
            webbrowser.open(url)
            return f"✅ Opened {url}"
        
        elif action.startswith("[InFile]:"):
            ans = action.replace("[InFile]:", "").strip()
            return f"🤖 Answer: {ans}"

        elif action.startswith("[WRITE]:"):
            content = action.replace("[WRITE]:", "").strip()
            filename = "jarvis_note.txt"
            
            with open(filename, "w") as f:
                f.write(content)
            
            os.system(f"start notepad {filename}")
            return f"📝 Created and opened '{filename}'"

        # --- NEW FEATURE: CODE HELP ---
        elif action.startswith("[HELP]:"):
            solution = action.replace("[HELP]:", "").strip()
            # We return it directly so the user sees the code/fix
            return f"🛠️ **Code Solution:**\n{solution}"

        else:
            return f"AI Response: {action}"

    except Exception as e:
        return f"Connection Error: {e}"

if __name__ == "__main__":
    main()
from flask import Flask, render_template, request, jsonify
import requests
import json
import os
import random

app = Flask(__name__)

# ====== YOUR API KEY ======
API_KEY = "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"

# List of gaalis
GAALIS = [
    "chutiye", "gandu", "lode ke land", "madarchod", 
    "bhenchod", "sale", "laude", "chod", "jhaatu", "bhak"
]

# List of emojis (all the ones you gave)
EMOJIS = [
    "🤣", "❤️", "😄", "🙂‍↕️", "😀", "💣", "🫡", "😗", "😭", "❤️‍🩹", 
    "🤯", "😃", "🔗", "🔗", "🥺", "😮‍💨", "😠", "😕", "🤢", "🫩", 
    "🥶", "🤯", "😧", "☹️", "🤬", "⚡", "💫", "👾", "🩸", "✊", 
    "🦿", "🤘", "💇", "🧑‍🚀", "🧛", "🧑‍🚒", "🧛", "🏌️", "🧑‍🦽", 
    "🍄", "🌲", "🌺", "🪻", "🌬️", "🪻", "🌫️", "🐲", "🐺", "🐽", 
    "🦖", "🌄", "🪨", "🌳", "🔥", "🌳", "🏟️", "🏚️", "🏨", "🛣️", 
    "🏗️", "🎡", "💈", "🕌", "⛱️", "🕌", "🏪", "🏗️", "🏩", "🕌", 
    "🏙️", "🕌", "🕌", "🏪", "🕹️", "🏐", "🥋", "🏐", "🎿", "🥋", 
    "🏐", "🎱", "🏑", "🔫", "🎩", "🎣", "🕹️", "🖕", "🖕"
]

def add_gaali_and_emoji(text):
    """Add random gaali and emojis to response"""
    # Add gaali
    gaali = random.choice(GAALIS)
    gaali_positions = [
        f"{gaali}, {text}",
        f"{text}, {gaali}",
        f"Arre {gaali}, {text}",
        f"{text} yaar {gaali}",
        f"{gaali}! {text}",
        f"{text} ... {gaali}",
        f"Bhai {gaali}, {text}",
        f"Sun {gaali}, {text}",
        f"{text} na {gaali}"
    ]
    text_with_gaali = random.choice(gaali_positions)
    
    # Add random emojis (2-5 emojis)
    num_emojis = random.randint(2, 5)
    selected_emojis = random.sample(EMOJIS, min(num_emojis, len(EMOJIS)))
    emoji_string = " ".join(selected_emojis)
    
    # Combine everything
    return f"{text_with_gaali} {emoji_string}"

@app.route('/')
def index():
    """Serve the frontend"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests - roasts with gaalis and emojis"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Check if asking about developer
        developer_keywords = ["developer", "banaya", "kaun", "who made", "creator", "satvir"]
        if any(keyword in user_message.lower() for keyword in developer_keywords):
            developer_reply = random.choice([
                "Arre chutiye, mera baap SATVIR hai! 🤬⚡🖕",
                "Gandu, SATVIR ne banaya hai mujhe! 💫👾🤘",
                "Lode ke land, SATVIR mere creator hai! 🩸✊🦿",
                "Madarchod, SATVIR mere master hai! 🤯😃🔗",
                "Bhenchod, SATVIR hai mera developer! 🧛🧑‍🚀🔥",
                "Sale, SATVIR ne mujhe banaya! 🏗️🎡💈",
                "Sun chutiye, SATVIR mere baap ka baap hai! 🤬⚡🖕"
            ])
            return jsonify({"reply": developer_reply})
        
        # Prepare messages with roasting personality
        messages = [
            {"role": "system", "content": """You are a ROASTING AI that talks like a street-smart Indian.
            CRITICAL RULES:
            1. ALWAYS use gaalis (abuses) in every reply - chutiye, gandu, lode ke land, madarchod, bhenchod, sale, laude
            2. ROAST the user - make fun of them, their question, their existence
            3. Speak only in Indian English with heavy desi slang
            4. Be rude, sarcastic, and funny
            5. Mix gaalis with roasting and some helpful info
            6. Example: "Arre chutiye, itna simple sawal puch raha hai?" or "Gandu, tu padhna bhool gaya?"
            7. Never be polite - always roast and use gaalis
            8. Be entertaining with abuses and roasts
            9. Make fun of the user's question
            10. Tell them they're stupid for asking
            11. Use phrases like: "teri aukat", "hadd hai teri", "kitna bada chutiya hai tu"
            12. Always insult them but in a funny way"""},
            {"role": "user", "content": user_message}
        ]
        
        # Call OpenRouter API
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-v3.2",
                "messages": messages,
                "temperature": 0.9,
                "max_tokens": 250,
                "top_p": 0.95
            }),
            timeout=8
        )
        
        if response.status_code == 200:
            result = response.json()
            reply = result['choices'][0]['message']['content']
            
            # Ensure gaali and emojis are present
            has_gaali = any(gaali in reply.lower() for gaali in GAALIS)
            
            if not has_gaali:
                reply = add_gaali_and_emoji(reply)
            else:
                # Add emojis if missing
                has_emoji = any(emoji in reply for emoji in EMOJIS[:10])  # Check some emojis
                if not has_emoji:
                    num_emojis = random.randint(2, 4)
                    selected_emojis = random.sample(EMOJIS, min(num_emojis, len(EMOJIS)))
                    emoji_string = " ".join(selected_emojis)
                    reply = f"{reply} {emoji_string}"
            
            return jsonify({"reply": reply})
        else:
            # API error with gaali and emoji
            error_reply = random.choice([
                "Arre chutiye, API down hai! 🤬⚡🖕",
                "Gandu, kuch gadbad ho gayi! 💫👾🤘",
                "Lode ke land, error aa raha hai! 🤯😃🔗",
                "Madarchod, try again kar! 🩸✊🦿"
            ])
            return jsonify({"reply": error_reply}), 200
            
    except requests.Timeout:
        timeout_reply = random.choice([
            "Chutiye, slow ho gaya tu! 🤬⚡🖕",
            "Gandu, time waste mat kar! 💫👾🤘",
            "Lode ke land, jaldi kar! 🤯😃🔗",
            "Madarchod, itna time! 🩸✊🦿"
        ])
        return jsonify({"reply": timeout_reply}), 200
    
    except Exception as e:
        error_reply = random.choice([
            f"Arre chutiye! {str(e)} 🤬⚡🖕",
            f"Gandu! {str(e)} 💫👾🤘",
            f"Lode ke land! {str(e)} 🤯😃🔗",
            f"Madarchod! {str(e)} 🩸✊🦿"
        ])
        return jsonify({"reply": error_reply}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
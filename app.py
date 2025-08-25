import os
from flask import Flask, request, jsonify
import requests
import logging


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WHATSAPP_CLOUD_API_VERSION = "v22.0"
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
YOUR_WEBSITE_URL = os.getenv("YOUR_WEBSITE_URL", "https://djahit.vercel.app/")

print(f"Environment variables loaded:")
print(f"VERIFY_TOKEN: {VERIFY_TOKEN}")
print(f"WHATSAPP_PHONE_NUMBER_ID: {'Set' if WHATSAPP_PHONE_NUMBER_ID else 'Not set'}")
print(f"WHATSAPP_ACCESS_TOKEN: {'Set' if WHATSAPP_ACCESS_TOKEN else 'Not set'}")
def send_payload(to_number, payload_data):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        **payload_data 
    }
    api_url = f"https://graph.facebook.com/{WHATSAPP_CLOUD_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Message sent successfully to {to_number}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to {to_number}: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        return False

def send_text_message(to_number, message_body):
    payload_data = {
        "type": "text",
        "text": {"body": message_body}
    }
    return send_payload(to_number, payload_data)

def send_welcome_menu(to_number, name):
    payload_data = {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "image",
                "image": {
                    "link": "https://i.imgur.com/2thSJby.png" 
                }
            },
            "body": {
                "text": f"Halo {name}! 👋\n\nSelamat datang di Djahit - layanan perbaikan dan jahit terpercaya! \n\nAda yang bisa kami bantu hari ini?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply", 
                        "reply": {
                            "id": "website", 
                            "title": "🌐 Website Kami"
                        }
                    },
                    {
                        "type": "reply", 
                        "reply": {
                            "id": "cek_antrean", 
                            "title": "📋 Cek Antrean"
                        }
                    },
                    {
                        "type": "reply", 
                        "reply": {
                            "id": "bantuan", 
                            "title": "🆘 Bantuan"
                        }
                    }
                ]
            },
            "footer": {
                "text": "Djahit: repair, don't replace! ✨"
            }
        }
    }
    return send_payload(to_number, payload_data)

def send_services_info(to_number):
    message = """🧵 *LAYANAN DJAHIT* 🧵

Kami menyediakan:
• Jahit baju custom
• Perbaikan pakaian 
• Sulam & bordir
• Alterasi ukuran
• Repair tas & sepatu

💻 Untuk melihat portfolio dan memesan layanan, kunjungi website kami!

Ketik "website" untuk mendapatkan link website kami."""
    
    return send_text_message(to_number, message)

def send_website_link(to_number):
    message = f"""🌐 *KUNJUNGI WEBSITE KAMI*

{YOUR_WEBSITE_URL}

Di website kami, Anda bisa:
• Melihat portfolio hasil jahitan
• Cek harga layanan
• Upload foto untuk estimasi
• Booking appointment
• Melihat testimoni customer

Terima kasih telah mempercayai Djahit! 🙏"""
    
    return send_text_message(to_number, message)

def send_queue_check_instruction(to_number):
    message = """📋 *CEK STATUS ANTREAN* (mohon maaf untuk saat ini layanan belum tersedia, COMING SOON ASAP)

Untuk mengecek status antrean Anda, silakan kirim nomor antrean dalam format angka.

Contoh: 123

Nomor antrean bisa Anda dapatkan saat melakukan booking di website atau datang langsung ke toko kami."""
    
    return send_text_message(to_number, message)

def send_help_info(to_number):
    message = f"""🆘 *BANTUAN & KONTAK*

Jam Operasional:
Senin - Sabtu: 08.00 - 17.00 WIB
Minggu: 09.00 - 15.00 WIB

📍 Alamat: Jl. Veteran No.10-11, Ketawanggede, Kec. Lowokwaru, Kota Malang, Jawa Timur 65145
📞 Telepon: +1 (555) 146-5080

Untuk informasi lengkap dan booking online:
{YOUR_WEBSITE_URL}

Ada pertanyaan lain? Ketik pesan Anda dan kami akan merespons secepatnya! 😊"""
    
    return send_text_message(to_number, message)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "WhatsApp Bot is running!",
        "status": "active",
        "endpoints": {
            "webhook": "/webhook"
        }
    })

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        logger.info(f"Verification attempt:")
        logger.info(f"  Mode: {mode}")
        logger.info(f"  Received token: {token}")
        logger.info(f"  Expected token: {VERIFY_TOKEN}")
        logger.info(f"  Challenge: {challenge}")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("Webhook verified successfully")
            return challenge, 200
        else:
            logger.error("Webhook verification failed")
            return "Verification failed", 403

    elif request.method == "POST":
        try:
            data = request.get_json()
            logger.info(f"Received webhook data: {data}")
            
            if not data or "object" not in data or "entry" not in data:
                return jsonify({"status": "ok"}), 200
            
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    if "messages" in value:
                        for message in value["messages"]:
                            from_number = message.get("from")
                            if not from_number:
                                continue
                                
                            name = "Customer"
                            contacts = value.get("contacts", [])
                            if contacts and "profile" in contacts[0]:
                                name = contacts[0]["profile"].get("name", "Customer")

                            message_type = message.get("type")
                            
                            if message_type == "text":
                                handle_text_message(from_number, message, name)
                            elif message_type == "interactive":
                                handle_interactive_message(from_number, message)
                            else:
                                send_text_message(from_number, 
                                    "Maaf, saat ini saya hanya dapat merespon pesan teks dan menu interaktif. Silakan pilih menu yang tersedia! 😊")

            return jsonify({"status": "ok"}), 200
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return jsonify({"status": "error"}), 500

    return jsonify({"error": "Method not allowed"}), 405
@app.route("/test", methods=["GET"])
def test():
    return jsonify({
        "status": "working",
        "verify_token": VERIFY_TOKEN,
        "port": os.environ.get("PORT", "5000"),
        "all_env_vars": dict(os.environ)
    })
def handle_text_message(from_number, message, name):
    message_body = message["text"]["body"].lower().strip()
    
    if message_body.isdigit():
        queue_number = message_body
        response = f"✅ Terima kasih! Sistem sedang mengecek status antrean nomor *{queue_number}*\n\n"
        response += "Status antrean Anda akan segera kami informasikan. Mohon tunggu sebentar ya! 🙏"
        send_text_message(from_number, response)
        return
    
    keywords_responses = {
        "website": lambda: send_website_link(from_number),
        "web": lambda: send_website_link(from_number),
        "layanan": lambda: send_services_info(from_number),
        "jasa": lambda: send_services_info(from_number),
        "bantuan": lambda: send_help_info(from_number),
        "help": lambda: send_help_info(from_number),
        "antrean": lambda: send_queue_check_instruction(from_number),
        "queue": lambda: send_queue_check_instruction(from_number),
    }
    
    for keyword, action in keywords_responses.items():
        if keyword in message_body:
            action()
            return
    
    send_welcome_menu(from_number, name)

def handle_interactive_message(from_number, message):
    interactive = message.get("interactive", {})
    
    if "button_reply" in interactive:
        button_id = interactive["button_reply"]["id"]
        
        if button_id == "website":
            send_website_link(from_number)
        elif button_id == "cek_antrean":
            send_queue_check_instruction(from_number)
        elif button_id == "bantuan":
            send_help_info(from_number)
        else:
            send_text_message(from_number, "Pilihan tidak dikenali. Silakan pilih dari menu yang tersedia.")
    
    elif "list_reply" in interactive:
        list_id = interactive["list_reply"]["id"]
        send_text_message(from_number, "Fitur ini akan segera tersedia. Silakan gunakan menu tombol untuk saat ini.")

if __name__ == "__main__":
    required_vars = [WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, VERIFY_TOKEN]
    if not all(required_vars):
        print("Missing required environment variables!")
        print("Please set: WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, VERIFY_TOKEN")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
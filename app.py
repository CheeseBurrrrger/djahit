import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- Configuration (from .env) ---
WHATSAPP_CLOUD_API_VERSION = "v22.0"
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# --- Helper Function to send a generic payload ---
def send_payload(to_number, payload_data):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        **payload_data # Unpack the custom payload data
    }
    api_url = f"https://graph.facebook.com/{WHATSAPP_CLOUD_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        print("Message sent successfully:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        if 'response' in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            print(f"Request payload: {payload}")  # Debug: print the payload
        else:
            print("No response received")
            print(f"Request payload: {payload}")

# --- Response Functions for different types ---
def send_text_message(to_number, message_body):
    payload_data = {
        "type": "text",
        "text": {"body": message_body}
    }
    send_payload(to_number, payload_data)

# Let's try a simpler approach first - just reply buttons to test
def send_interactive_menu_simple(to_number, name):
    payload_data = {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "image",
                "image": {
                    "link": "https://i.imgur.com/8nDrSzm.jpeg" 
                }
            },
            "body": {
                "text": f"Haloo dear {name}! Terimakasih sudah menghubungi Djahit, Ada yang bisa kami bantu?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply", 
                        "reply": {
                            "id": "website", 
                            "title": "Website Kami"
                        }
                    },
                    {
                        "type": "reply", 
                        "reply": {
                            "id": "cek_antrean", 
                            "title": "Cek antrean"
                        }
                    },
                    {
                        "type": "reply", 
                        "reply": {
                            "id": "bantuan", 
                            "title": "Bantuan"
                        }
                    }
                ]
            },
            "footer": {
                "text": "Djahit: repair, don't replace!"
            }
        }
    }
    send_payload(to_number, payload_data)

# CORRECT format for mixing URL and reply buttons (this should work!)
def send_interactive_menu(to_number, name):
    payload_data = {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": f"Haloo dear {name}! Terimakasih sudah menghubungi Djahit, Ada yang bisa kami bantu?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "url", 
                        "title": "Website Kami",
                        "url": "https://icn-filkom.ub.ac.id/  "
                    },
                    {
                        "type": "reply", 
                        "reply": {
                            "id": "cek_antrean", 
                            "title": "Cek antrean"
                        }
                    },
                    {
                        "type": "reply", 
                        "reply": {
                            "id": "bantuan", 
                            "title": "feel lost?"
                        }
                    }
                ]
            },
            "footer": {
                "text": "Djahit: repair, don't replace!"
            }
        }
    }
    send_payload(to_number, payload_data)

# # Alternative: Interactive menu with list instead of buttons
# def send_interactive_list_menu(to_number, name):
#     payload_data = {
#         "type": "interactive",
#         "interactive": {
#             "type": "list",
#             "body": {
#                 "text": f"Haloo dear {name}! Terimakasih sudah menghubungi Djahit, Ada beberapa hal yang dapat kami bantu"
#             },
#             "action": {
#                 "button": "Pilih Menu",
#                 "sections": [
#                     {
#                         "title": "Layanan Kami",
#                         "rows": [
#                             {"id": "cek_antrean", "title": "Cek Antrean", "description": "Cek status antrean Anda"},
#                             {"id": "lihat_jasa", "title": "Lihat Jasa", "description": "Lihat layanan yang tersedia"},
#                             {"id": "bantuan", "title": "Bantuan", "description": "Butuh bantuan?"}
#                         ]
#                     }
#                 ]
#             },
#             "footer": {
#                 "text": "Djahit: repair, don't replace!"
#             }
#         }
#     }
#     send_payload(to_number, payload_data)

# Fixed video message function
def send_video_message(to_number):
    payload_data = {
        "type": "video",
        "video": {
            "link": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4  ",  # Using a more reliable sample video
            "caption": "Ini video dari kami!"
        }
    }
    send_payload(to_number, payload_data)

# Function to send website link as text message
def send_website_link(to_number):
    message = "Kunjungi website kami \n https://icn-filkom.ub.ac.id/   untuk informasi lebih lengkap!"
    send_text_message(to_number, message)

# --- Main Webhook Endpoint ---
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            print("WEBHOOK_VERIFICATION_FAILED: Token mismatch or invalid mode.")
            return "Verification token mismatch or invalid mode", 403

    elif request.method == "POST":
        data = request.get_json()
        print(f"Received webhook data: {data}")  # Debug: print incoming data
        
        if "object" in data and "entry" in data:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    if "messages" in change["value"]:
                        for message in change["value"]["messages"]:
                            from_number = message["from"]
                            name = change["value"]["contacts"][0]["profile"]["name"]

                            # Check for text messages and interactive replies
                            if message["type"] == "text":
                                message_body = message["text"]["body"].lower()
                                if "video" in message_body or "vidio" in message_body:
                                    send_video_message(from_number)
                                elif "website" in message_body or "web" in message_body:
                                    send_website_link(from_number)
                                elif message_body.isdigit():
                                    send_text_message(from_number,"Terimakasih atas jawaban anda, sistem akan segera melacak nomor antrean anda")
                                else:
                                    # Try simple version first to debug
                                    send_interactive_menu_simple(from_number, name)
                            elif message["type"] == "interactive":
                                # Handle button replies
                                if "button_reply" in message["interactive"]:
                                    button_id = message["interactive"]["button_reply"]["id"]    
                                    if button_id == "cek_antrean":
                                        send_text_message(from_number, "Baik, Mohon dapat dibantu kirim nomor antrean anda (masukkan dalam angka)")
                                    elif button_id == "lihat_jasa":
                                        send_text_message(from_number, "Berikut adalah beberapa jasa yang kami tawarkan:\n1. Jahit baju\n2. Sulam\n3. Reparasi\n4. Alterasi")
                                    elif button_id == "bantuan":
                                        send_text_message(from_number, "Silakan hubungi customer service kami atau ketik 'website' untuk informasi lebih lanjut")
                                    elif button_id == "website":
                                        send_text_message(from_number, "Kunjungi website kami \nhttps://icn-filkom.ub.ac.id/ \nuntuk informasi lebih lengkap!")
                                    else:
                                        send_text_message(from_number, "Pilihan tidak dikenali. Silakan pilih dari menu yang tersedia.")
                                # Handle list replies
                                elif "list_reply" in message["interactive"]:
                                    list_id = message["interactive"]["list_reply"]["id"]
                                    if list_id == "cek_antrean":
                                        send_text_message(from_number, "Baik, Mohon dapat dibantu kirim nomor antrean anda (masukkan dalam angka)")
                                    elif list_id == "lihat_jasa":
                                        send_text_message(from_number, "Berikut adalah beberapa jasa yang kami tawarkan:\n1. Jahit baju\n2. Sulam\n3. Reparasi\n4. Alterasi")
                                    elif list_id == "bantuan":
                                        send_text_message(from_number, "Silakan hubungi customer service kami atau ketik 'website' untuk informasi lebih lanjut")
                                    else:
                                        send_text_message(from_number, "Pilihan tidak dikenali. Silakan pilih dari menu yang tersedia.")
                            else:
                                send_text_message(from_number, "Maaf, saya hanya bisa merespon pesan teks dan tombol interaktif untuk saat ini.")

        return jsonify({"status": "ok"}), 200
    return "Method not allowed", 405

if __name__ == "__main__":
    if not all([WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, VERIFY_TOKEN]):
        print("--- CONFIGURATION WARNING ---")
        print("Please set your environment variables in the .env file.")
        print("-----------------------------")
    app.run(debug=True, port=5000)
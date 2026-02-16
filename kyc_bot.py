import speech_recognition as sr # type: ignore
import pyttsx3# type: ignore
import json
from datetime import datetime
import re
import os


class KYCVoiceBot:
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.session_data = {
            "session_id": f"kyc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "user_data": {},
            "verification_status": "pending",
            "attempts": {}
        }
        self.max_retries = 2
    
    def speak(self, text: str) -> None:
       
        print(f"\n Bot: {text}")
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        del engine
    
    def listen(self, timeout: int = 5) -> tuple[str | None, str]:
        
        try:
            with sr.Microphone() as source:
                print(" Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
                text = self.recognizer.recognize_google(audio)
                print(f" You said: {text}")
                return text.strip(), "success"
                
        except sr.WaitTimeoutError:
            return None, "timeout"
        except sr.UnknownValueError:
            return None, "unclear"
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None, "error"
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None, "error"
    
    def validate_name(self, name: str) -> bool:
        
        if not name or len(name.strip()) < 2:
            return False
        return bool(re.match(r'^[A-Za-z\s.]+$', name))
    
    def validate_phone(self, phone: str) -> bool:
       
        phone_digits = re.sub(r'\D', '', phone)
        return len(phone_digits) == 10 and phone_digits.isdigit()
    
    def validate_pan(self, pan: str) -> bool:
     
        pan = pan.replace(" ", "").upper()
        
        if len(pan) != 10 or not pan.isalnum():
            return False
        
       
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
        return bool(re.match(pattern, pan))
    
    def validate_consent(self, response: str) -> bool | None:
        
        response = response.lower().strip()
        
        if any(word in response for word in ['yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'agree']):
            return True
        
        if any(word in response for word in ['no', 'nope', 'not', 'don\'t', 'dont']):
            return False
        
        return None
    
    def collect_field(self, field_name: str, prompt: str, validator, error_message: str) -> str | None:
        
        attempts = 0
        
        while attempts <= self.max_retries:
            self.speak(prompt)
            user_input, status = self.listen()
            
            if status == "timeout":
                if attempts < self.max_retries:
                    self.speak("I didn't hear anything. Let me try again.")
                    attempts += 1
                    continue
                else:
                    self.speak("I'm having trouble hearing you. Let's try this field later.")
                    return None
            
            elif status == "unclear":
                if attempts < self.max_retries:
                    self.speak("I didn't catch that clearly. Could you please repeat?")
                    attempts += 1
                    continue
                else:
                    self.speak("I'm sorry, I'm having trouble understanding. Let's move on.")
                    return None
            
            elif status == "error":
                self.speak("I'm experiencing technical difficulties. Please try again.")
                attempts += 1
                continue
            
            if user_input and validator(user_input):
                self.session_data["attempts"][field_name] = attempts + 1
                return user_input
            else:
                if attempts < self.max_retries:
                    self.speak(error_message)
                    attempts += 1
                else:
                    self.speak(f"I couldn't verify your {field_name} after multiple attempts.")
                    return None
        
        return None
    
    def collect_consent(self) -> bool:
       
        attempts = 0
        
        while attempts <= self.max_retries:
            self.speak("Do you consent to this KYC verification? Please say yes or no.")
            response, status = self.listen()
            
            if status == "timeout" or status == "unclear":
                if attempts < self.max_retries:
                    self.speak("I didn't hear you clearly. Please say yes or no.")
                    attempts += 1
                    continue
                else:
                    self.speak("I couldn't confirm your consent. Ending verification.")
                    return False
            
            if response:
                consent = self.validate_consent(response)
                
                if consent is True:
                    self.session_data["attempts"]["consent"] = attempts + 1
                    return True
                elif consent is False:
                    self.speak("You have not provided consent. We cannot proceed with verification. Thank you.")
                    return False
                else:
                    if attempts < self.max_retries:
                        self.speak("Please respond with yes or no only.")
                        attempts += 1
                    else:
                        self.speak("I couldn't understand your response. Ending verification.")
                        return False
            
            attempts += 1
        
        return False
    
    def collect_kyc_data(self) -> bool:
        
        self.speak("Welcome to Decentro KYC verification. This call may be recorded for quality and compliance purposes.")
        
        name = self.collect_field(
            "name",
            "May I have your full name please?",
            self.validate_name,
            "I need a valid name with at least two characters. Please provide your full name."
        )
        
        if not name:
            self.speak("Unable to proceed without a valid name. Thank you for your time.")
            return False
        
        self.session_data["user_data"]["name"] = name
        
        phone = self.collect_field(
            "phone",
            "Thank you. What is your 10-digit phone number?",
            self.validate_phone,
            "Please provide a valid 10-digit phone number."
        )
        
        if not phone:
            self.speak("Unable to proceed without a valid phone number. Thank you for your time.")
            return False
        
        self.session_data["user_data"]["phone"] = re.sub(r'\D', '', phone)
        
        pan = self.collect_field(
            "pan",
            "Please provide your PAN number. That's 5 letters, followed by 4 digits, and 1 letter.",
            self.validate_pan,
            "Please provide a valid PAN number with 10 alphanumeric characters."
        )
        
        if not pan:
            self.speak("Unable to proceed without a valid PAN. Thank you for your time.")
            return False
        
        self.session_data["user_data"]["pan"] = pan.replace(" ", "").upper()
        
        consent = self.collect_consent()
        
        if not consent:
            self.session_data["user_data"]["consent"] = False
            self.session_data["verification_status"] = "consent_declined"
            return False
        
        self.session_data["user_data"]["consent"] = True
        
        self.speak(f"Thank you. Let me confirm your details. Name: {name}. "
                  f"Phone number: {self.session_data['user_data']['phone']}. "
                  f"PAN: {self.session_data['user_data']['pan']}. "
                  f"Consent: provided.")
        
        self.session_data["verification_status"] = "completed"
        
        self.speak("Your KYC verification is complete. A confirmation will be sent to your registered phone number. Thank you for choosing Decentro.")
        
        return True
    
    def save_session(self, filename: str = None) -> str:
        
        if filename is None:
            os.makedirs("output", exist_ok=True)
            filename = f"output/kyc_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.session_data, f, indent=2)
        
        print(f"\n Session saved to: {filename}")
        return filename
    
    def run(self) -> None:
        try:
            print("\n" + "="*60)
            print("  DECENTRO KYC VERIFICATION SYSTEM")
            print("="*60)
            print("\nPlease ensure:")
            print("  ✓ Your microphone is working")
            print("  ✓ You're in a quiet environment")
            print("  ✓ You speak clearly\n")
            
            input("Press Enter when ready to start...")
            print()
            
            success = self.collect_kyc_data()
            
            output_file = self.save_session()
            
            print("\n" + "="*60)
            if success:
                print("   KYC VERIFICATION COMPLETED SUCCESSFULLY")
            else:
                print("   KYC VERIFICATION INCOMPLETE")
            print("="*60)
            print(f"\nSession details saved to: {output_file}")
            
        except KeyboardInterrupt:
            print("\n\n  Verification cancelled by user.")
            self.session_data["verification_status"] = "cancelled"
            self.save_session()
        except Exception as e:
            print(f"\n Unexpected error: {e}")
            self.session_data["verification_status"] = "error"
            self.save_session()


def main():
    bot = KYCVoiceBot()
    bot.run()


if __name__ == "__main__":
    main()


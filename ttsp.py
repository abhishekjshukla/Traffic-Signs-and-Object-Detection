# import pyttsx3
# engine = pyttsx3.init()
# engine.say('Sally sells seashells by the seashore.')
# engine.say('The quick brown fox jumped over the lazy dog.')
# engine.runAndWait()
from gtts import gTTS
tts = gTTS(text='Please Stop', lang='en')
tts.save("Stop_en.mp3")
# Transcription Maker Project

## Overview
This project creates realistic video/podcast transcriptions from text files using the Gemini LLM model.

## Requirements
1. Read text files from a specified input folder
2. Process each file through the Gemini LLM API with a prompt that converts the content into a transcript format
3. Save the generated transcripts to a local output folder

## Implementation Steps
1. Set up a file reader to scan the input directory for .txt files
2. For each file:
    - Extract the content and identify the topic
    - Create a well-crafted prompt for the LLM that specifies transcript-style formatting
    - Send the request to the Gemini API
    - Save the response as a new transcript file in the output directory
3. Include error handling for API failures or file access issues

## Prompt Engineering
The prompt should instruct Gemini to:
- Format the response as a natural spoken transcript
- Include speaker indicators if appropriate
- Maintain all key information from the source file
- Adopt a conversational, educational tone

## API Integration
We'll use the Gemini API's structured output capabilities as documented at [Google AI Gemini API docs](https://ai.google.dev/gemini-api/docs/structured-output?lang=python) to ensure consistent transcript formatting.

## Audio Generation
After creating transcripts, we'll implement audio generation:

1. Read transcript files from the transcripts folder
2. Feed content into a TTS (Text-to-Speech) model running locally
3. Generate audio segments from the transcript text
4. Merge all audio segments into a single file
5. Save the final audio file to the "audios" folder

## Implementation Files
We'll create two Python files for this project:
1. `transcript_to_audio.py` - Main script to process transcripts and coordinate audio generation
2. `tts_generator.py` - Module handling the text-to-speech conversion using a local model

```py
# 1️⃣ Install kokoro
!pip install -q kokoro>=0.8.4 soundfile
# 2️⃣ Install espeak, used for English OOD fallback and some non-English languages
!apt-get -qq -y install espeak-ng > /dev/null 2>&1
# 🇪🇸 'e' => Spanish es
# 🇫🇷 'f' => French fr-fr
# 🇮🇳 'h' => Hindi hi
# 🇮🇹 'i' => Italian it
# 🇧🇷 'p' => Brazilian Portuguese pt-br

# 3️⃣ Initalize a pipeline
from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import torch
# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]
pipeline = KPipeline(lang_code='a') # <= make sure lang_code matches voice

# This text is for demonstration purposes only, unseen during training
text = '''
The sky above the port was the color of television, tuned to a dead channel.
"It's not like I'm using," Case heard someone say, as he shouldered his way through the crowd around the door of the Chat. "It's like my body's developed this massive drug deficiency."
It was a Sprawl voice and a Sprawl joke. The Chatsubo was a bar for professional expatriates; you could drink there for a week and never hear two words in Japanese.

These were to have an enormous impact, not only because they were associated with Constantine, but also because, as in so many other areas, the decisions taken by Constantine (or in his name) were to have great significance for centuries to come. One of the main issues was the shape that Christian churches were to take, since there was not, apparently, a tradition of monumental church buildings when Constantine decided to help the Christian church build a series of truly spectacular structures. The main form that these churches took was that of the basilica, a multipurpose rectangular structure, based ultimately on the earlier Greek stoa, which could be found in most of the great cities of the empire. Christianity, unlike classical polytheism, needed a large interior space for the celebration of its religious services, and the basilica aptly filled that need. We naturally do not know the degree to which the emperor was involved in the design of new churches, but it is tempting to connect this with the secular basilica that Constantine completed in the Roman forum (the so-called Basilica of Maxentius) and the one he probably built in Trier, in connection with his residence in the city at a time when he was still caesar.

[Kokoro](/kˈOkəɹO/) is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models while being significantly faster and more cost-efficient. With Apache-licensed weights, [Kokoro](/kˈOkəɹO/) can be deployed anywhere from production environments to personal projects.
'''
# text = '「もしおれがただ偶然、そしてこうしようというつもりでなくここに立っているのなら、ちょっとばかり絶望するところだな」と、そんなことが彼の頭に思い浮かんだ。'
# text = '中國人民不信邪也不怕邪，不惹事也不怕事，任何外國不要指望我們會拿自己的核心利益做交易，不要指望我們會吞下損害我國主權、安全、發展利益的苦果！'
# text = 'Los partidos políticos tradicionales compiten con los populismos y los movimientos asamblearios.'
# text = 'Le dromadaire resplendissant déambulait tranquillement dans les méandres en mastiquant de petites feuilles vernissées.'
# text = 'ट्रांसपोर्टरों की हड़ताल लगातार पांचवें दिन जारी, दिसंबर से इलेक्ट्रॉनिक टोल कलेक्शनल सिस्टम'
# text = "Allora cominciava l'insonnia, o un dormiveglia peggiore dell'insonnia, che talvolta assumeva i caratteri dell'incubo."
# text = 'Elabora relatórios de acompanhamento cronológico para as diferentes unidades do Departamento que propõem contratos.'

# 4️⃣ Generate, display, and save audio files in a loop.
generator = pipeline(
    text, voice='af_heart', # <= change voice here
    speed=1, split_pattern=r'\n+'
)

# Alternatively, load voice tensor directly:
voice_tensor = torch.load('path/to/voice.pt', weights_only=True)
generator = pipeline(
    text, voice=voice_tensor,
    speed=1, split_pattern=r'\n+'
)

for i, (gs, ps, audio) in enumerate(generator):
    print(i)  # i => index
    print(gs) # gs => graphemes/text
    print(ps) # ps => phonemes
    display(Audio(data=audio, rate=24000, autoplay=i==0))
    sf.write(f'{i}.wav', audio, 24000) # save each audio file
```
# """
# NEXUS Voice Interface Layer
# Implements client-side, zero-cost, browser-native Speech-to-Text and Text-to-Speech
# via standard Web Speech API (webkitSpeechRecognition & speechSynthesis).
# 100% Streamlit Cloud compatible with zero external paid API keys.
# Includes full audio playback control: Play, Pause, Stop, and Speech cancellation.
# """

# VOICE_INTERFACE_HTML = """
# <div style="background: rgba(17, 24, 39, 0.85); border: 1px solid #1E293B; border-radius: 12px; padding: 16px; margin: 10px 0; color: #F8FAFC; font-family: sans-serif;">
#   <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
#     <div style="display: flex; align-items: center; gap: 8px;">
#       <span style="font-size: 1.2rem;">🎤</span>
#       <span style="font-weight: 600; color: #22D3EE; font-size: 0.95rem;">VOICE INTERACTION // TALK TO NEXUS</span>
#     </div>
#     <span id="voice-status" style="font-size: 0.8rem; color: #94A3B8; background: #0D1220; padding: 4px 10px; border-radius: 20px; border: 1px solid #1E293B;">Ready</span>
#   </div>
  
#   <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
#     <button id="start-listen-btn" style="background: linear-gradient(135deg, #6366F1, #4F46E5); color: #FFF; border: none; border-radius: 8px; padding: 8px 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;">
#       <span>🎙️</span> <span id="listen-btn-text">Speak Scenario</span>
#     </button>
#     <button id="readout-btn" style="background: #0D1220; color: #22D3EE; border: 1px solid #22D3EE; border-radius: 8px; padding: 8px 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;">
#       <span id="readout-icon">🔊</span> <span id="readout-btn-text">Listen to Executive Briefing</span>
#     </button>
#     <button id="stop-audio-btn" style="background: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid #EF4444; border-radius: 8px; padding: 8px 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;">
#       <span>⏹️</span> <span>Stop Audio</span>
#     </button>
#   </div>
  
#   <div id="transcript-container" style="margin-top: 12px; display: none; background: #070A13; border: 1px solid #1E293B; border-radius: 8px; padding: 10px;">
#     <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; margin-bottom: 4px;">Detected Speech:</div>
#     <div id="voice-text" style="color: #F8FAFC; font-size: 0.9rem; font-weight: 500;"></div>
#     <div style="margin-top: 6px; font-size: 0.75rem; color: #22C55E;">✓ Transcribed successfully. Copy or type into scenario box below.</div>
#   </div>
# </div>

# <script>
# (function() {
#   const statusEl = document.getElementById('voice-status');
#   const listenBtn = document.getElementById('start-listen-btn');
#   const listenBtnText = document.getElementById('listen-btn-text');
#   const readoutBtn = document.getElementById('readout-btn');
#   const readoutBtnText = document.getElementById('readout-btn-text');
#   const readoutIcon = document.getElementById('readout-icon');
#   const stopAudioBtn = document.getElementById('stop-audio-btn');
#   const transcriptContainer = document.getElementById('transcript-container');
#   const voiceText = document.getElementById('voice-text');
  
#   let recognition = null;
#   let isListening = false;
#   let isSpeaking = false;
  
#   // Clean cancellation helper
#   function stopAllSpeech() {
#     if (window.speechSynthesis) {
#       window.speechSynthesis.cancel();
#     }
#     isSpeaking = false;
#     readoutIcon.textContent = '🔊';
#     readoutBtnText.textContent = 'Listen to Executive Briefing';
#     readoutBtn.style.borderColor = '#22D3EE';
#     readoutBtn.style.color = '#22D3EE';
#     statusEl.textContent = 'Audio Stopped';
#     statusEl.style.color = '#94A3B8';
#     statusEl.style.borderColor = '#1E293B';
#   }
  
#   // Stop button handler
#   stopAudioBtn.addEventListener('click', function() {
#     stopAllSpeech();
#   });
  
#   // Always stop speaking if page unloads or re-runs
#   window.addEventListener('beforeunload', function() {
#     if (window.speechSynthesis) {
#       window.speechSynthesis.cancel();
#     }
#   });

#   // Speech Recognition (Speech to Text)
#   const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
#   if (SpeechRecognition) {
#     recognition = new SpeechRecognition();
#     recognition.continuous = false;
#     recognition.interimResults = true;
#     recognition.lang = 'en-US';
    
#     recognition.onstart = function() {
#       // If audio is playing when user wants to speak, stop audio
#       stopAllSpeech();
#       isListening = true;
#       statusEl.textContent = 'Listening...';
#       statusEl.style.color = '#EF4444';
#       statusEl.style.borderColor = '#EF4444';
#       listenBtnText.textContent = 'Stop Listening';
#     };
    
#     recognition.onresult = function(event) {
#       let interim = '';
#       let final = '';
#       for (let i = event.resultIndex; i < event.results.length; ++i) {
#         if (event.results[i].isFinal) {
#           final += event.results[i][0].transcript;
#         } else {
#           interim += event.results[i][0].transcript;
#         }
#       }
#       const transcript = final || interim;
#       if (transcript) {
#         transcriptContainer.style.display = 'block';
#         voiceText.textContent = transcript;
        
#         try {
#           const inputs = window.parent.document.querySelectorAll('input[type="text"]');
#           inputs.forEach(input => {
#             if (input.placeholder && input.placeholder.includes('Supplier A')) {
#               input.value = transcript;
#               input.dispatchEvent(new Event('input', { bubbles: true }));
#             }
#           });
#         } catch(e) {}
#       }
#     };
    
#     recognition.onerror = function(event) {
#       statusEl.textContent = 'Speech error: ' + event.error;
#       statusEl.style.color = '#F59E0B';
#       isListening = false;
#       listenBtnText.textContent = 'Speak Scenario';
#     };
    
#     recognition.onend = function() {
#       isListening = false;
#       statusEl.textContent = 'Speech Captured';
#       statusEl.style.color = '#22C55E';
#       statusEl.style.borderColor = '#22C55E';
#       listenBtnText.textContent = 'Speak Scenario';
#     };
#   } else {
#     statusEl.textContent = 'Web Speech not supported';
#   }
  
#   listenBtn.addEventListener('click', function() {
#     if (!recognition) {
#       alert('Speech Recognition is not supported by your browser. Please use Chrome, Edge, or Safari.');
#       return;
#     }
#     if (isListening) {
#       recognition.stop();
#     } else {
#       recognition.start();
#     }
#   });
  
#   // Speech Synthesis (Text to Speech) with Toggle & Stop capability
#   readoutBtn.addEventListener('click', function() {
#     if (!window.speechSynthesis) {
#       alert('Text to speech is not supported in this browser.');
#       return;
#     }
    
#     // If currently speaking, toggle to stop!
#     if (window.speechSynthesis.speaking && isSpeaking) {
#       stopAllSpeech();
#       return;
#     }
    
#     // Find impact text from parent document or read default briefing
#     let textToSpeak = "NEXUS Executive Briefing. ";
#     try {
#       const summaryEl = window.parent.document.querySelector('.executive-briefing-text');
#       if (summaryEl && summaryEl.innerText && summaryEl.innerText.trim().length > 10) {
#         // Strip markdown asterisks and hashtags for smooth speech
#         let cleanText = summaryEl.innerText
#           .replace(/[*#_`]/g, '')
#           .replace(/\n+/g, '. ')
#           .replace(/\s+/g, ' ');
#         textToSpeak += cleanText;
#       } else {
#         textToSpeak += "Simulation complete. Evaluated failure cascade and inventory buffer across all dependent processes and finished products.";
#       }
#     } catch(e) {
#       textToSpeak += "Simulation complete. Production chain evaluated with deterministic impact results.";
#     }
    
#     // Cancel any previous utterances
#     window.speechSynthesis.cancel();
    
#     const utterance = new SpeechSynthesisUtterance(textToSpeak);
#     utterance.rate = 1.05;
#     utterance.pitch = 1.0;
    
#     utterance.onstart = function() {
#       isSpeaking = true;
#       readoutIcon.textContent = '⏹️';
#       readoutBtnText.textContent = 'Stop Speaking';
#       readoutBtn.style.borderColor = '#EF4444';
#       readoutBtn.style.color = '#EF4444';
#       statusEl.textContent = 'Playing Audio Briefing... (Click to Stop)';
#       statusEl.style.color = '#22D3EE';
#       statusEl.style.borderColor = '#22D3EE';
#     };
    
#     utterance.onend = function() {
#       stopAllSpeech();
#       statusEl.textContent = 'Briefing Finished';
#       statusEl.style.color = '#94A3B8';
#     };
    
#     utterance.onerror = function() {
#       stopAllSpeech();
#     };
    
#     window.speechSynthesis.speak(utterance);
#   });
# })();
# </script>
# """


# def render_voice_interface():
#     """Returns HTML for voice interface component."""
#     return VOICE_INTERFACE_HTML



"""
NEXUS Voice Interface Layer

Provides:
- Browser-based Speech-to-Text for the "Speak Scenario" button.
- Browser-based Text-to-Speech for the executive briefing.
- A Streamlit-compatible voice panel.
- No paid voice API required.

Important:
The voice panel is an interface layer only.
It does not replace the NEXUS scenario-analysis pipeline.
"""

import streamlit as st
import streamlit.components.v1 as components


VOICE_PANEL_HTML = """
<div style="
    background: rgba(17, 24, 39, 0.88);
    border: 1px solid #1E293B;
    border-radius: 14px;
    padding: 16px;
    margin: 10px 0;
    color: #F8FAFC;
    font-family: Arial, sans-serif;
">

    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 8px;
        ">
            <span style="font-size: 1.2rem;">🎤</span>

            <span style="
                font-weight: 700;
                color: #22D3EE;
                font-size: 0.95rem;
            ">
                VOICE INTERACTION // TALK TO NEXUS
            </span>
        </div>

        <span id="nexus-voice-status" style="
            font-size: 0.75rem;
            color: #94A3B8;
            background: #0D1220;
            padding: 5px 10px;
            border-radius: 20px;
            border: 1px solid #1E293B;
        ">
            Ready
        </span>
    </div>


    <div style="
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        align-items: center;
    ">

        <button id="nexus-speak-btn" style="
            background: linear-gradient(135deg, #6366F1, #4F46E5);
            color: white;
            border: none;
            border-radius: 9px;
            padding: 9px 16px;
            font-weight: 700;
            cursor: pointer;
            font-size: 0.88rem;
        ">
            🎙️ Speak Scenario
        </button>


        <button id="nexus-stop-listening-btn" style="
            display: none;
            background: rgba(239, 68, 68, 0.15);
            color: #EF4444;
            border: 1px solid #EF4444;
            border-radius: 9px;
            padding: 9px 16px;
            font-weight: 700;
            cursor: pointer;
            font-size: 0.88rem;
        ">
            ⏹ Stop Listening
        </button>


        <button id="nexus-readout-btn" style="
            background: #0D1220;
            color: #22D3EE;
            border: 1px solid #22D3EE;
            border-radius: 9px;
            padding: 9px 16px;
            font-weight: 700;
            cursor: pointer;
            font-size: 0.88rem;
        ">
            🔊 Listen to Executive Briefing
        </button>


        <button id="nexus-stop-audio-btn" style="
            background: rgba(239, 68, 68, 0.12);
            color: #EF4444;
            border: 1px solid #EF4444;
            border-radius: 9px;
            padding: 9px 16px;
            font-weight: 700;
            cursor: pointer;
            font-size: 0.88rem;
        ">
            ⏹ Stop Audio
        </button>

    </div>


    <div id="nexus-transcript-box" style="
        display: none;
        margin-top: 12px;
        background: #070A13;
        border: 1px solid #1E293B;
        border-radius: 9px;
        padding: 12px;
    ">

        <div style="
            font-size: 0.72rem;
            color: #94A3B8;
            text-transform: uppercase;
            margin-bottom: 5px;
        ">
            Detected Speech
        </div>

        <div id="nexus-transcript" style="
            color: #F8FAFC;
            font-size: 0.9rem;
            font-weight: 500;
            line-height: 1.5;
        ">
        </div>

        <div style="
            margin-top: 7px;
            font-size: 0.72rem;
            color: #22C55E;
        ">
            ✓ Speech captured. Review the scenario field before running the simulation.
        </div>

    </div>

</div>


<script>

(function () {

    const statusEl =
        document.getElementById("nexus-voice-status");

    const speakBtn =
        document.getElementById("nexus-speak-btn");

    const stopListeningBtn =
        document.getElementById("nexus-stop-listening-btn");

    const readoutBtn =
        document.getElementById("nexus-readout-btn");

    const stopAudioBtn =
        document.getElementById("nexus-stop-audio-btn");

    const transcriptBox =
        document.getElementById("nexus-transcript-box");

    const transcriptEl =
        document.getElementById("nexus-transcript");


    let recognition = null;
    let listening = false;


    function setStatus(text, color) {

        statusEl.textContent = text;
        statusEl.style.color = color;

    }


    function findScenarioInput() {

        try {

            const inputs =
                window.parent.document.querySelectorAll(
                    "input, textarea"
                );

            for (const input of inputs) {

                const placeholder =
                    (input.getAttribute("placeholder") || "")
                    .toLowerCase();

                if (
                    placeholder.includes("supplier") ||
                    placeholder.includes("scenario") ||
                    placeholder.includes("what happens") ||
                    placeholder.includes("failure")
                ) {

                    return input;

                }

            }

        } catch (error) {

            console.log("Could not access parent input:", error);

        }

        return null;

    }


    function putTranscriptIntoScenario(text) {

        const input = findScenarioInput();

        if (!input) {
            return;
        }

        try {

            const nativeSetter =
                Object.getOwnPropertyDescriptor(
                    input.tagName === "TEXTAREA"
                        ? HTMLTextAreaElement.prototype
                        : HTMLInputElement.prototype,
                    "value"
                );

            if (nativeSetter && nativeSetter.set) {

                nativeSetter.set.call(input, text);

            } else {

                input.value = text;

            }

            input.dispatchEvent(
                new Event("input", {
                    bubbles: true
                })
            );

            input.dispatchEvent(
                new Event("change", {
                    bubbles: true
                })
            );

        } catch (error) {

            console.log(
                "Could not update Streamlit scenario input:",
                error
            );

        }

    }


    function stopRecognition() {

        if (recognition && listening) {

            try {
                recognition.stop();
            } catch (error) {
                console.log(error);
            }

        }

    }


    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    if (SpeechRecognition) {

        recognition = new SpeechRecognition();

        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = "en-US";


        recognition.onstart = function () {

            listening = true;

            speakBtn.style.display = "none";
            stopListeningBtn.style.display = "inline-block";

            setStatus(
                "Listening...",
                "#EF4444"
            );

        };


        recognition.onresult = function (event) {

            let transcript = "";

            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                transcript +=
                    event.results[i][0].transcript;

            }

            transcript = transcript.trim();

            if (transcript) {

                transcriptBox.style.display = "block";
                transcriptEl.textContent = transcript;

                putTranscriptIntoScenario(transcript);

            }

        };


        recognition.onerror = function (event) {

            listening = false;

            speakBtn.style.display = "inline-block";
            stopListeningBtn.style.display = "none";

            setStatus(
                "Speech error: " + event.error,
                "#F59E0B"
            );

        };


        recognition.onend = function () {

            listening = false;

            speakBtn.style.display = "inline-block";
            stopListeningBtn.style.display = "none";

            setStatus(
                "Speech Captured",
                "#22C55E"
            );

        };


        speakBtn.addEventListener(
            "click",
            function () {

                if (listening) {
                    stopRecognition();
                    return;
                }

                try {

                    recognition.start();

                } catch (error) {

                    setStatus(
                        "Microphone unavailable",
                        "#F59E0B"
                    );

                }

            }
        );


        stopListeningBtn.addEventListener(
            "click",
            function () {

                stopRecognition();

            }
        );


    } else {

        speakBtn.disabled = true;

        speakBtn.style.opacity = "0.5";
        speakBtn.style.cursor = "not-allowed";

        setStatus(
            "Speech not supported",
            "#F59E0B"
        );

    }


    readoutBtn.addEventListener(
        "click",
        function () {

            if (!window.speechSynthesis) {

                alert(
                    "Text-to-speech is not supported by this browser."
                );

                return;

            }


            if (window.speechSynthesis.speaking) {

                window.speechSynthesis.cancel();

                readoutBtn.textContent =
                    "🔊 Listen to Executive Briefing";

                setStatus(
                    "Audio Stopped",
                    "#94A3B8"
                );

                return;

            }


            let textToSpeak =
                "NEXUS Executive Briefing. ";


            try {

                const briefing =
                    window.parent.document.querySelector(
                        ".executive-briefing-text"
                    );

                if (
                    briefing &&
                    briefing.innerText &&
                    briefing.innerText.trim().length > 5
                ) {

                    textToSpeak +=
                        briefing.innerText
                            .replace(/[*#_`]/g, "")
                            .replace(/\\n+/g, ". ")
                            .replace(/\\s+/g, " ")
                            .trim();

                } else {

                    textToSpeak +=
                        "Simulation complete. " +
                        "NEXUS evaluated the dependency graph " +
                        "and identified the resulting impact.";

                }

            } catch (error) {

                textToSpeak +=
                    "Simulation complete. " +
                    "NEXUS evaluated the dependency graph.";

            }


            window.speechSynthesis.cancel();


            const utterance =
                new SpeechSynthesisUtterance(
                    textToSpeak
                );


            utterance.rate = 1.05;
            utterance.pitch = 1.0;


            utterance.onstart = function () {

                readoutBtn.textContent =
                    "⏹ Stop Speaking";

                setStatus(
                    "Playing briefing...",
                    "#22D3EE"
                );

            };


            utterance.onend = function () {

                readoutBtn.textContent =
                    "🔊 Listen to Executive Briefing";

                setStatus(
                    "Briefing Finished",
                    "#94A3B8"
                );

            };


            utterance.onerror = function () {

                readoutBtn.textContent =
                    "🔊 Listen to Executive Briefing";

                setStatus(
                    "Audio error",
                    "#F59E0B"
                );

            };


            window.speechSynthesis.speak(
                utterance
            );

        }
    );


    stopAudioBtn.addEventListener(
        "click",
        function () {

            if (window.speechSynthesis) {

                window.speechSynthesis.cancel();

            }

            readoutBtn.textContent =
                "🔊 Listen to Executive Briefing";

            setStatus(
                "Audio Stopped",
                "#94A3B8"
            );

        }
    );


})();

</script>
"""


def render_voice_panel(briefing_text=None):
    """
    Render the NEXUS voice interaction panel.

    Parameters
    ----------
    briefing_text : str | None
        Optional executive briefing text. The browser-side
        interface will attempt to read the visible briefing
        from the page; this parameter is retained so app.py
        can pass the scenario narrative without breaking
        the function interface.
    """

    components.html(
        VOICE_PANEL_HTML,
        height=220,
        scrolling=False,
    )


def render_voice_interface():
    """
    Backward-compatible alias.

    Kept so older code importing render_voice_interface()
    does not immediately break.
    """

    return VOICE_PANEL_HTML


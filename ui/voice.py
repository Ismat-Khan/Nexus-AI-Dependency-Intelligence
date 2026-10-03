"""
NEXUS Voice Interface Layer

Provides:
- Continuous browser Speech-to-Text
- Browser Text-to-Speech
- Streamlit-compatible voice panel
- No paid voice API required
"""

import streamlit.components.v1 as components


VOICE_PANEL_HTML = """
<div style="
    background: rgba(17, 24, 39, 0.92);
    border: 1px solid #1E293B;
    border-radius: 14px;
    padding: 16px;
    margin: 10px 0;
    color: #F8FAFC;
    font-family: Arial, sans-serif;
">

    <div style="
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom:12px;
    ">
        <div style="
            display:flex;
            align-items:center;
            gap:8px;
        ">
            <span style="font-size:1.2rem;">🎤</span>

            <span style="
                font-weight:700;
                color:#22D3EE;
                font-size:0.95rem;
            ">
                VOICE INTERACTION // TALK TO NEXUS
            </span>
        </div>

        <span id="nexus-voice-status" style="
            font-size:0.75rem;
            color:#94A3B8;
            background:#0D1220;
            padding:5px 10px;
            border-radius:20px;
            border:1px solid #1E293B;
        ">
            Ready
        </span>
    </div>


    <div style="
        display:flex;
        gap:10px;
        flex-wrap:wrap;
        align-items:center;
    ">

        <button id="nexus-speak-btn" style="
            background:linear-gradient(135deg,#6366F1,#4F46E5);
            color:white;
            border:none;
            border-radius:9px;
            padding:9px 16px;
            font-weight:700;
            cursor:pointer;
            font-size:0.88rem;
        ">
            🎙️ Speak Scenario
        </button>


        <button id="nexus-stop-listening-btn" style="
            display:none;
            background:rgba(239,68,68,0.15);
            color:#EF4444;
            border:1px solid #EF4444;
            border-radius:9px;
            padding:9px 16px;
            font-weight:700;
            cursor:pointer;
            font-size:0.88rem;
        ">
            ⏹ Stop Listening
        </button>


        <button id="nexus-readout-btn" style="
            background:#0D1220;
            color:#22D3EE;
            border:1px solid #22D3EE;
            border-radius:9px;
            padding:9px 16px;
            font-weight:700;
            cursor:pointer;
            font-size:0.88rem;
        ">
            🔊 Listen to Executive Briefing
        </button>


        <button id="nexus-stop-audio-btn" style="
            background:rgba(239,68,68,0.12);
            color:#EF4444;
            border:1px solid #EF4444;
            border-radius:9px;
            padding:9px 16px;
            font-weight:700;
            cursor:pointer;
            font-size:0.88rem;
        ">
            ⏹ Stop Audio
        </button>

    </div>


    <div id="nexus-transcript-box" style="
        display:none;
        margin-top:12px;
        background:#070A13;
        border:1px solid #1E293B;
        border-radius:9px;
        padding:12px;
    ">

        <div style="
            font-size:0.72rem;
            color:#94A3B8;
            text-transform:uppercase;
            margin-bottom:5px;
        ">
            Detected Speech
        </div>

        <div id="nexus-transcript" style="
            color:#F8FAFC;
            font-size:0.9rem;
            font-weight:500;
            line-height:1.5;
        "></div>

        <div style="
            margin-top:7px;
            font-size:0.72rem;
            color:#22C55E;
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

    let manuallyStopped = false;

    let finalTranscript = "";

    let restartTimer = null;


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
                    (
                        input.getAttribute("placeholder") || ""
                    ).toLowerCase();

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

            console.log(
                "Could not access parent input:",
                error
            );
        }

        return null;
    }


    function putTranscriptIntoScenario(text) {

        const input = findScenarioInput();

        if (!input) {
            return;
        }

        try {

            const prototype =
                input.tagName === "TEXTAREA"
                    ? HTMLTextAreaElement.prototype
                    : HTMLInputElement.prototype;

            const descriptor =
                Object.getOwnPropertyDescriptor(
                    prototype,
                    "value"
                );

            if (descriptor && descriptor.set) {

                descriptor.set.call(
                    input,
                    text
                );

            } else {

                input.value = text;
            }


            input.dispatchEvent(
                new Event(
                    "input",
                    {
                        bubbles: true
                    }
                )
            );


            input.dispatchEvent(
                new Event(
                    "change",
                    {
                        bubbles: true
                    }
                )
            );

        } catch (error) {

            console.log(
                "Could not update scenario input:",
                error
            );
        }
    }


    function displayTranscript(text) {

        if (!text) {
            return;
        }

        transcriptBox.style.display = "block";

        transcriptEl.textContent = text;

        putTranscriptIntoScenario(text);
    }


    function createRecognition() {

        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;


        if (!SpeechRecognition) {
            return null;
        }


        const instance =
            new SpeechRecognition();


        /*
         * IMPORTANT:
         * Continuous mode allows longer scenario sentences.
         */
        instance.continuous = true;

        /*
         * Keep interim results so the user can see
         * the words while speaking.
         */
        instance.interimResults = true;

        /*
         * More suitable for normal English speech.
         */
        instance.lang = "en-US";

        /*
         * Ask the browser for alternatives.
         * The first result remains the primary transcript.
         */
        instance.maxAlternatives = 1;


        instance.onstart = function () {

            listening = true;

            speakBtn.style.display = "none";

            stopListeningBtn.style.display =
                "inline-block";

            setStatus(
                "Listening... Keep speaking",
                "#EF4444"
            );
        };


        instance.onresult = function (event) {

            let interimTranscript = "";

            let newFinalTranscript = "";


            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                const result =
                    event.results[i];

                const transcript =
                    result[0].transcript;


                if (result.isFinal) {

                    newFinalTranscript +=
                        transcript + " ";

                } else {

                    interimTranscript +=
                        transcript;
                }
            }


            /*
             * Add only newly finalized speech.
             */
            if (newFinalTranscript) {

                finalTranscript +=
                    newFinalTranscript;
            }


            const combinedTranscript =
                (
                    finalTranscript +
                    interimTranscript
                ).trim();


            if (combinedTranscript) {

                displayTranscript(
                    combinedTranscript
                );
            }
        };


        instance.onerror = function (event) {

            /*
             * Some browsers report "no-speech"
             * when there was simply a short pause.
             *
             * We do NOT stop the whole voice session.
             */
            if (
                event.error === "no-speech" ||
                event.error === "audio-capture"
            ) {

                setStatus(
                    "Listening...",
                    "#EF4444"
                );

                return;
            }


            console.log(
                "Speech recognition error:",
                event.error
            );

            setStatus(
                "Speech error: " + event.error,
                "#F59E0B"
            );
        };


        instance.onend = function () {

            listening = false;


            /*
             * Chrome/Edge may automatically end a
             * recognition session even when the user
             * still wants to speak.
             *
             * Restart automatically unless the user
             * explicitly pressed Stop Listening.
             */
            if (!manuallyStopped) {

                setStatus(
                    "Reconnecting microphone...",
                    "#22D3EE"
                );


                clearTimeout(
                    restartTimer
                );


                restartTimer =
                    setTimeout(
                        function () {

                            if (
                                !manuallyStopped &&
                                recognition
                            ) {

                                try {

                                    recognition.start();

                                } catch (error) {

                                    console.log(
                                        "Recognition restart:",
                                        error
                                    );
                                }
                            }

                        },
                        250
                    );


                return;
            }


            speakBtn.style.display =
                "inline-block";

            stopListeningBtn.style.display =
                "none";


            setStatus(
                "Speech Captured",
                "#22C55E"
            );
        };


        return instance;
    }


    /*
     * Initialize browser recognition.
     */
    recognition =
        createRecognition();


    if (!recognition) {

        speakBtn.disabled = true;

        speakBtn.style.opacity = "0.5";

        speakBtn.style.cursor =
            "not-allowed";

        setStatus(
            "Speech not supported",
            "#F59E0B"
        );

    } else {


        /*
         * START LISTENING
         */
        speakBtn.addEventListener(
            "click",
            function () {

                if (listening) {
                    return;
                }


                /*
                 * Start a completely fresh transcript.
                 */
                finalTranscript = "";

                transcriptEl.textContent = "";

                transcriptBox.style.display =
                    "none";


                manuallyStopped = false;


                clearTimeout(
                    restartTimer
                );


                try {

                    recognition.start();

                } catch (error) {

                    console.log(
                        "Recognition start:",
                        error
                    );

                    setStatus(
                        "Microphone unavailable",
                        "#F59E0B"
                    );
                }
            }
        );


        /*
         * STOP LISTENING
         */
        stopListeningBtn.addEventListener(
            "click",
            function () {

                manuallyStopped = true;

                clearTimeout(
                    restartTimer
                );


                if (recognition) {

                    try {
                        recognition.stop();
                    } catch (error) {
                        console.log(error);
                    }
                }


                listening = false;


                speakBtn.style.display =
                    "inline-block";

                stopListeningBtn.style.display =
                    "none";


                setStatus(
                    "Speech Captured",
                    "#22C55E"
                );
            }
        );
    }


    /*
     * TEXT TO SPEECH
     */
    readoutBtn.addEventListener(
        "click",
        function () {

            if (!window.speechSynthesis) {

                alert(
                    "Text-to-speech is not supported by this browser."
                );

                return;
            }


            if (
                window.speechSynthesis.speaking
            ) {

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


            utterance.onstart =
                function () {

                    readoutBtn.textContent =
                        "⏹ Stop Speaking";


                    setStatus(
                        "Playing briefing...",
                        "#22D3EE"
                    );
                };


            utterance.onend =
                function () {

                    readoutBtn.textContent =
                        "🔊 Listen to Executive Briefing";


                    setStatus(
                        "Briefing Finished",
                        "#94A3B8"
                    );
                };


            utterance.onerror =
                function () {

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


    /*
     * STOP AUDIO
     */
    stopAudioBtn.addEventListener(
        "click",
        function () {

            if (
                window.speechSynthesis
            ) {

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
    """

    components.html(
        VOICE_PANEL_HTML,
        height=220,
        scrolling=False,
    )


def render_voice_interface():
    """
    Backward-compatible function for older imports.
    """

    return VOICE_PANEL_HTML

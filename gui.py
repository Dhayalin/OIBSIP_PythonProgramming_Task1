"""
Graphical User Interface for Nova Assistant.
Built with CustomTkinter — emerald green + dark gray theme.
"""

import threading

import customtkinter as ctk

from commands import process_command
from utils import (
    APP_NAME,
    APP_TAGLINE,
    MIC_CHECKING,
    MIC_CONNECTED,
    MIC_DISCONNECTED,
    STATUS_ERROR,
    STATUS_IDLE,
    STATUS_LISTENING,
    STATUS_PROCESSING,
    STATUS_SPEAKING,
    get_current_date,
    get_current_time,
)
from voice import VoiceEngine


# --- Appearance settings ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Emerald Green + Dark Gray palette
COLOR_BG = "#1c1c1e"
COLOR_SURFACE = "#2c2c2e"
COLOR_SURFACE_LIGHT = "#3a3a3c"
COLOR_ACCENT = "#10b981"
COLOR_PRIMARY = "#059669"
COLOR_HIGHLIGHT = "#34d399"
COLOR_TEXT = "#f5f5f5"
COLOR_MUTED = "#9ca3af"
COLOR_USER_BUBBLE = "#065f46"
COLOR_BOT_BUBBLE = "#3a3a3c"
COLOR_WARNING = "#f59e0b"
COLOR_SPEAKING = "#6ee7b7"
COLOR_ERROR = "#ef4444"

# Sound-wave bar labels for the logo (ASCII, no emoji)
WAVEFORM_CHARS = ("|", "||", "|||", "||||", "|||", "||", "|")


class VoiceAssistantGUI(ctk.CTk):
    """Main application window for Nova Assistant."""

    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("900x950")
        self.minsize(700, 800)
        self.configure(fg_color=COLOR_BG)

        

        # Voice engine and state flags
        self.voice = VoiceEngine()
        self.is_listening = False
        self.should_stop = False
        self.last_command = "None"
        self.mic_status = MIC_CHECKING
        self._pulse_step = 0
        self._dots_step = 0
        self._pulse_job = None
        self._dots_job = None
        self._clock_job = None

        self._build_ui()
        self._start_clock()
        self._initialize_microphone()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Create all widgets and lay them out."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=8)

        self._build_header()
        self._build_info_panel()
        self._build_mic_section()
        self._build_controls()
        self._build_chat_area()
        self._build_footer()

        self._add_message(
            "assistant",
            f"Hello! I'm {APP_NAME}. Click 'Start Listening' or tap the microphone to begin.",
        )

    def _build_header(self):
        """Logo (mic + waveform), title, and tagline."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(18, 4), sticky="ew")

        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.pack()

        # Microphone icon inside a circular ring
        mic_ring = ctk.CTkFrame(
            logo_frame,
            width=72,
            height=72,
            corner_radius=36,
            fg_color=COLOR_SURFACE,
            border_width=2,
            border_color=COLOR_ACCENT,
        )
        mic_ring.pack(side="left", padx=(0, 10))
        mic_ring.pack_propagate(False)

        ctk.CTkLabel(
            mic_ring,
            text="MIC",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_ACCENT,
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Animated-style sound wave bars (static visual)
        wave_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        wave_frame.pack(side="left", pady=8)

        self.wave_labels = []
        for char in WAVEFORM_CHARS:
            lbl = ctk.CTkLabel(
                wave_frame,
                text=char,
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=COLOR_ACCENT,
            )
            lbl.pack(side="left", padx=1)
            self.wave_labels.append(lbl)

        title_label = ctk.CTkLabel(
            header,
            text=APP_NAME,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_HIGHLIGHT,
        )
        title_label.pack(pady=(10, 0))

        ctk.CTkLabel(
            header,
            text=APP_TAGLINE,
            font=ctk.CTkFont(size=13),
            text_color=COLOR_MUTED,
        ).pack()

    def _build_info_panel(self):
        """Rich status panel with live date/time and mic info."""
        panel = ctk.CTkFrame(
            self,
            fg_color=COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_SURFACE_LIGHT,
        )
        panel.grid(row=1, column=0, padx=24, pady=(10, 6), sticky="ew")
        panel.grid_columnconfigure((0, 1), weight=1)

        label_font = ctk.CTkFont(size=12)
        value_font = ctk.CTkFont(size=12, weight="bold")

        def add_row(row, col, label_text, default_value, color=COLOR_TEXT):
            frame = ctk.CTkFrame(panel, fg_color="transparent")
            frame.grid(row=row, column=col, padx=14, pady=6, sticky="w")
            ctk.CTkLabel(frame, text=label_text, font=label_font, text_color=COLOR_MUTED).pack(anchor="w")
            val = ctk.CTkLabel(frame, text=default_value, font=value_font, text_color=color)
            val.pack(anchor="w")
            return val

        self.status_value = add_row(0, 0, "Status", STATUS_IDLE, COLOR_ACCENT)
        self.mic_value = add_row(0, 1, "Microphone", MIC_CHECKING, COLOR_MUTED)
        self.last_cmd_value = add_row(1, 0, "Last Command", "None", COLOR_TEXT)
        self.date_value = add_row(1, 1, "Today's Date", get_current_date(), COLOR_TEXT)
        self.time_value = add_row(2, 0, "Current Time", get_current_time(), COLOR_HIGHLIGHT)

    def _build_mic_section(self):
        """Large microphone button with listening animation label."""
        mic_section = ctk.CTkFrame(self, fg_color="transparent")
        mic_section.grid(row=2, column=0, pady=(4,0))

        self.mic_button = ctk.CTkButton(
            mic_section,
            text="MIC",
            font=ctk.CTkFont(size=18, weight="bold"),
            width=110,
            height=110,
            corner_radius=55,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_ACCENT,
            border_width=3,
            border_color=COLOR_ACCENT,
            command=self._toggle_listening,
        )
        self.mic_button.pack()

        self.listening_label = ctk.CTkLabel(
            mic_section,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_ACCENT,
        )
        self.listening_label.pack(pady=(6, 0))

    def _build_controls(self):
        """Start, Stop, Clear, and Exit buttons."""
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=3, column=0, padx=24, pady=(2,2), sticky="new")

        btn_style = {"height": 38, "font": ctk.CTkFont(size=13, weight="bold")}

        self.start_button = ctk.CTkButton(
            controls,
            text="Start Listening",
            width=155,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_ACCENT,
            command=self._start_listening,
            **btn_style,
        )
        self.start_button.grid(row=0, column=0, padx=(0, 6))

        self.stop_button = ctk.CTkButton(
            controls,
            text="Stop",
            width=90,
            fg_color=COLOR_SURFACE_LIGHT,
            hover_color="#555555",
            command=self._stop_listening,
            state="disabled",
            **btn_style,
        )
        self.stop_button.grid(row=0, column=1, padx=(0, 6))

        self.clear_button = ctk.CTkButton(
            controls,
            text="Clear Chat",
            width=110,
            fg_color=COLOR_SURFACE,
            hover_color=COLOR_SURFACE_LIGHT,
            command=self._clear_chat,
            **btn_style,
        )
        self.clear_button.grid(row=0, column=2, padx=(0, 6))

        self.exit_button = ctk.CTkButton(
            controls,
            text="Exit",
            width=80,
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            command=self._exit_app,
            **btn_style,
        )
        self.exit_button.grid(row=0, column=3)

    def _build_chat_area(self):
        """Scrollable chat area with bubble-style messages."""
        chat_outer = ctk.CTkFrame(
            self,
            fg_color=COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_SURFACE_LIGHT,
            height=420
        )
        chat_outer.grid(row=5, column=0, padx=20, pady=(2,4), sticky="nsew")
        chat_outer.grid_propagate(False)
        chat_outer.grid_columnconfigure(0, weight=1)
        chat_outer.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            chat_outer,
            text="Conversation",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_MUTED,
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")

        self.chat_scroll = ctk.CTkScrollableFrame(
            chat_outer,
            fg_color=COLOR_BG,
            corner_radius=8,
            height=380
        )
        self.chat_scroll.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
    def _build_footer(self):
        """Application footer."""

        footer = ctk.CTkFrame(
            self,
            fg_color=COLOR_SURFACE,
            corner_radius=0,
            height=64,
        )
        footer.grid(row=6, column=0, sticky="ew")
        footer.grid_propagate(False)

        ctk.CTkLabel(
            footer,
            text=APP_NAME,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_HIGHLIGHT,
        ).pack(pady=(10, 2))

        ctk.CTkLabel(
            footer,
            text="Powered by Python • SpeechRecognition • pyttsx3",
            font=ctk.CTkFont(size=10),
            text_color=COLOR_MUTED,
        ).pack()



    # ------------------------------------------------------------------
    # Live Clock
    # ------------------------------------------------------------------

    def _start_clock(self):
        """Update date and time labels every second."""
        self.date_value.configure(text=get_current_date())
        self.time_value.configure(text=get_current_time())
        self._clock_job = self.after(1000, self._start_clock)

    # ------------------------------------------------------------------
    # Microphone Initialization
    # ------------------------------------------------------------------

    def _initialize_microphone(self):
        """Check microphone availability on startup (runs in a thread)."""
        def _check():
            success, message = self.voice.initialize_microphone()
            if success:
                self.mic_status = MIC_CONNECTED
                self.after(0, lambda: self._set_mic_status(MIC_CONNECTED, COLOR_ACCENT))
                self.after(0, lambda: self._add_message("assistant", message))
            else:
                self.mic_status = MIC_DISCONNECTED
                self.after(0, lambda: self._set_mic_status(MIC_DISCONNECTED, COLOR_ERROR))
                self.after(0, lambda: self._set_status(STATUS_ERROR))
                self.after(0, lambda: self._add_message("assistant", f"Warning: {message}"))

        threading.Thread(target=_check, daemon=True).start()

    def _set_mic_status(self, status: str, color: str):
        """Update the microphone status in the info panel."""
        self.mic_status = status
        self.mic_value.configure(text=status, text_color=color)

    # ------------------------------------------------------------------
    # Animations
    # ------------------------------------------------------------------

    def _start_listening_animation(self):
        """Pulse the mic button and animate waveform + dots."""
        self._pulse_step = 0
        self._dots_step = 0
        self._pulse_mic()
        self._animate_dots()
        self._animate_waveform()

    def _stop_listening_animation(self):
        """Cancel all listening animations."""
        if self._pulse_job:
            self.after_cancel(self._pulse_job)
            self._pulse_job = None
        if self._dots_job:
            self.after_cancel(self._dots_job)
            self._dots_job = None
        self.listening_label.configure(text="")
        self.mic_button.configure(
            fg_color=COLOR_PRIMARY,
            border_color=COLOR_ACCENT,
            width=110,
            height=110,
        )
        for lbl in self.wave_labels:
            lbl.configure(text_color=COLOR_ACCENT)

    def _pulse_mic(self):
        """Animate the microphone without resizing it."""

        if not self.is_listening:
            return

        colors = [
            COLOR_PRIMARY,
            COLOR_ACCENT,
            COLOR_HIGHLIGHT,
            COLOR_ACCENT,
        ]

        idx = self._pulse_step % len(colors)

        self.mic_button.configure(
            fg_color=colors[idx],
            border_color=COLOR_HIGHLIGHT,
        )

        self._pulse_step += 1
        self._pulse_job = self.after(400, self._pulse_mic)
    def _animate_dots(self):
        """Show animated dots while listening."""
        if not self.is_listening:
            return

        patterns = [
            "Listening.",
            "Listening..",
            "Listening..."
        ]
        self.listening_label.configure(text=patterns[self._dots_step % 3])
        self._dots_step += 1
        self._dots_job = self.after(400, self._animate_dots)

    def _animate_waveform(self):
        """Cycle waveform bar colors while listening."""
        if not self.is_listening:
            return

        bright = COLOR_HIGHLIGHT
        dim = COLOR_PRIMARY
        for i, lbl in enumerate(self.wave_labels):
            lbl.configure(text_color=bright if (self._pulse_step + i) % 3 == 0 else dim)

        self.after(200, self._animate_waveform)

    # ------------------------------------------------------------------
    # Listening Control
    # ------------------------------------------------------------------

    def _toggle_listening(self):
        if self.is_listening:
            self._stop_listening()
        else:
            self._start_listening()

    def _start_listening(self):
        if self.is_listening:
            return

        self.is_listening = True
        self.should_stop = False
        self._set_status(STATUS_LISTENING)
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self._start_listening_animation()

        threading.Thread(target=self._listening_loop, daemon=True).start()

    def _stop_listening(self):
        self.should_stop = True
        self.is_listening = False
        self.voice.stop_speaking()
        self._set_status(STATUS_IDLE)
        self._stop_listening_animation()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def _listening_loop(self):
        """Main voice loop — runs in a background thread."""
        while self.is_listening and not self.should_stop:
            self.after(0, lambda: self._set_status(STATUS_LISTENING))
            success, result = self.voice.listen()

            if self.should_stop:
                break

            if not success:
                self.after(0, lambda msg=result: self._add_message("assistant", msg))
                continue

            self.after(0, lambda text=result: self._add_message("user", text))

            self.after(0, lambda: self._set_status(STATUS_PROCESSING))
            response, should_exit = process_command(result)

            self.after(0, lambda text=response: self._add_message("assistant", text))
            self.after(0, lambda: self._set_status(STATUS_SPEAKING))
            self.voice.speak(response)

            if should_exit:
                self.after(500, self._exit_app)
                break

        self.after(0, self._reset_controls)

    def _reset_controls(self):
        self.is_listening = False
        self._set_status(STATUS_IDLE)
        self._stop_listening_animation()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    # ------------------------------------------------------------------
    # Chat Bubbles
    # ------------------------------------------------------------------

    def _add_message(self, sender: str, text: str):
        """Add a styled chat bubble to the scrollable conversation area."""
        is_user = sender == "user"

        if is_user:
            self.last_command = text
            self.last_cmd_value.configure(text=text)

        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", padx=6, pady=5, anchor="e" if is_user else "w")

        bubble = ctk.CTkFrame(
            row,
            fg_color=COLOR_USER_BUBBLE if is_user else COLOR_BOT_BUBBLE,
            corner_radius=14,
            border_width=1,
            border_color=COLOR_ACCENT if not is_user else COLOR_PRIMARY,
        )
        bubble.pack(anchor="e" if is_user else "w", padx=(40, 0) if not is_user else (0, 40))

        header_text = "You" if is_user else APP_NAME
        ctk.CTkLabel(
            bubble,
            text=header_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLOR_HIGHLIGHT if not is_user else "#a7f3d0",
        ).pack(anchor="w", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            bubble,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color=COLOR_TEXT,
            wraplength=440,
            justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 12))

        # Auto-scroll to the latest message
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def _clear_chat(self):
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()
        self.last_command = "None"
        self.last_cmd_value.configure(text="None")
        self._add_message("assistant", "Chat cleared. Ready for new commands!")

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def _set_status(self, status: str):
        """Update the status field in the info panel."""
        color_map = {
            STATUS_IDLE: COLOR_ACCENT,
            STATUS_LISTENING: COLOR_HIGHLIGHT,
            STATUS_PROCESSING: COLOR_WARNING,
            STATUS_SPEAKING: COLOR_SPEAKING,
            STATUS_ERROR: COLOR_ERROR,
        }
        self.status_value.configure(text=status, text_color=color_map.get(status, COLOR_MUTED))

    def _exit_app(self):
        self.should_stop = True
        self.is_listening = False
        if self._clock_job:
            self.after_cancel(self._clock_job)
        self._stop_listening_animation()
        self.voice.stop_speaking()
        self.destroy()

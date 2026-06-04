"""ViviDoc Video Demo — Time Dilation

A standalone Manim script demonstrating the ViviDoc video generation style.
Topic: Special Relativity — Time Dilation (a Parameter Exploration case).

Scenes
------
  Scene 1 — TimeDilationIntro          : Title card + topic overview
  Scene 2 — LorentzFactorDerivation    : Lorentz factor γ = 1/√(1−β²) derived step-by-step
  Scene 3 — LorentzFactorCurve         : γ vs β curve with ValueTracker dot
  Scene 4 — LightClockAnimation        : Bouncing photon in a moving light clock
  Scene 5 — TimeDilationConclusion     : Key takeaways

Render
------
    manim render examples/video_demo.py TimeDilationDoc --quality medium

Or render all five scenes individually:
    manim render examples/video_demo.py -a --quality medium

Requirements
------------
    pip install manim>=0.18.0
"""

from manim import *
import numpy as np


# ============================================================================
# Scene 1 — Introduction
# ============================================================================


class TimeDilationIntro(Scene):
    """Title card and motivating question for time dilation."""

    def construct(self):
        # Topic title
        title = Text("Time Dilation", font_size=60, weight=BOLD)
        subtitle = Text(
            "How motion slows the passage of time",
            font_size=30,
            color=GREY_B,
        )
        subtitle.next_to(title, DOWN, buff=0.4)

        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle, shift=UP * 0.3))
        self.wait(1.5)

        # Motivating question
        question = Text(
            "If you travel fast enough,\ndoes time actually slow down?",
            font_size=28,
            color=YELLOW,
            line_spacing=1.4,
        ).shift(DOWN * 1.5)

        self.play(FadeOut(subtitle), Write(question), run_time=1.5)
        self.wait(1)

        # Einstein attribution
        einstein = Text(
            "— Special Relativity, Albert Einstein (1905)",
            font_size=20,
            color=GREY_C,
            slant=ITALIC,
        ).to_edge(DOWN)
        self.play(FadeIn(einstein))
        self.wait(2)

        self.play(FadeOut(title), FadeOut(question), FadeOut(einstein))


# ============================================================================
# Scene 2 — Lorentz Factor Derivation
# ============================================================================


class LorentzFactorDerivation(Scene):
    """Derive γ = 1 / √(1 − v²/c²) step by step."""

    def construct(self):
        section_label = Text("The Lorentz Factor", font_size=40, weight=BOLD).to_edge(UP)
        self.play(Write(section_label))
        self.wait(0.5)

        # Step 1 — introduce β = v/c
        step1_label = Text("Step 1: Define β (beta)", font_size=28, color=BLUE_C)
        step1_label.shift(UP * 1.5)
        beta_def = MathTex(r"\beta = \frac{v}{c}", font_size=48)
        beta_desc = Text(
            "β is the fraction of the speed of light", font_size=22, color=GREY_B
        ).next_to(beta_def, DOWN, buff=0.3)

        self.play(Write(step1_label))
        self.play(Write(beta_def))
        self.play(FadeIn(beta_desc))
        self.wait(1.5)

        # Step 2 — the time dilation raw form
        step2_label = Text("Step 2: Time dilation", font_size=28, color=BLUE_C)
        step2_label.shift(UP * 1.5)
        dilation_raw = MathTex(
            r"\Delta t' = \frac{\Delta t}{\sqrt{1 - v^2/c^2}}",
            font_size=44,
        )

        self.play(
            Transform(step1_label, step2_label),
            FadeOut(beta_def),
            FadeOut(beta_desc),
        )
        self.play(Write(dilation_raw))
        self.wait(1.5)

        # Step 3 — substitute β
        step3_label = Text("Step 3: Factor out γ", font_size=28, color=BLUE_C)
        step3_label.shift(UP * 1.5)
        gamma_def = MathTex(
            r"\gamma = \frac{1}{\sqrt{1 - \beta^2}}", font_size=52, color=YELLOW
        )
        gamma_box = SurroundingRectangle(gamma_def, color=YELLOW, buff=0.3)
        final_eq = MathTex(r"\Delta t' = \gamma \, \Delta t", font_size=44)
        final_eq.next_to(gamma_def, DOWN, buff=0.8)

        self.play(
            Transform(step1_label, step3_label),
            FadeOut(dilation_raw),
        )
        self.play(Write(gamma_def), run_time=2)
        self.play(Create(gamma_box))
        self.play(Write(final_eq))
        self.wait(0.5)

        # Constraint highlight
        constraint = Text(
            "γ ≥ 1 always  →  time can only slow down, never speed up",
            font_size=24,
            color=GREEN_C,
        ).to_edge(DOWN, buff=0.6)
        self.play(Write(constraint))
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])


# ============================================================================
# Scene 3 — γ vs β Curve with ValueTracker
# ============================================================================


class LorentzFactorCurve(Scene):
    """Animate the γ vs β curve and show a dot tracking β with always_redraw."""

    def construct(self):
        section_label = Text("γ as a function of β", font_size=36, weight=BOLD).to_edge(UP)
        self.play(Write(section_label))

        # Axes
        axes = Axes(
            x_range=[0, 1.0, 0.2],
            y_range=[1, 10, 2],
            x_length=8,
            y_length=5,
            axis_config={"include_tip": True},
            x_axis_config={"numbers_to_include": [0.2, 0.4, 0.6, 0.8, 1.0]},
            y_axis_config={"numbers_to_include": [2, 4, 6, 8]},
        ).shift(DOWN * 0.3)

        x_label = axes.get_x_axis_label(MathTex(r"\beta = v/c"), direction=RIGHT)
        y_label = axes.get_y_axis_label(MathTex(r"\gamma"), direction=UP)

        self.play(Create(axes), Write(x_label), Write(y_label))

        # Plot the γ(β) curve up to β = 0.99
        def gamma(beta):
            return 1.0 / np.sqrt(max(1e-9, 1 - beta**2))

        curve = axes.plot(gamma, x_range=[0, 0.99, 0.001], color=BLUE, stroke_width=3)
        self.play(Create(curve), run_time=2.5)
        self.wait(0.5)

        # ValueTracker for β
        beta_tracker = ValueTracker(0.01)

        # Moving dot on the curve
        moving_dot = always_redraw(
            lambda: Dot(
                axes.i2gp(beta_tracker.get_value(), curve),
                color=YELLOW,
                radius=0.1,
            )
        )

        # Live readout labels
        beta_label = always_redraw(
            lambda: MathTex(
                r"\beta = " + f"{beta_tracker.get_value():.3f}",
                font_size=32,
                color=YELLOW,
            ).to_corner(DL).shift(UP * 0.5 + RIGHT * 0.5)
        )

        gamma_label = always_redraw(
            lambda: MathTex(
                r"\gamma = " + f"{gamma(beta_tracker.get_value()):.2f}",
                font_size=32,
                color=GREEN_C,
            ).next_to(beta_label, UP, buff=0.3)
        )

        self.add(moving_dot, beta_label, gamma_label)
        self.wait(0.5)

        # Sweep β from 0 → 0.5 slowly
        self.play(beta_tracker.animate.set_value(0.5), run_time=3, rate_func=smooth)
        self.wait(0.8)

        # Sweep β from 0.5 → 0.9
        self.play(beta_tracker.animate.set_value(0.9), run_time=3, rate_func=smooth)
        self.wait(0.8)

        # Sweep β from 0.9 → 0.99 (curve shoots to infinity)
        self.play(beta_tracker.animate.set_value(0.99), run_time=2, rate_func=smooth)
        self.wait(1)

        # Constraint annotation
        constraint = Text(
            "As β → 1,  γ → ∞  →  time stops for the traveler",
            font_size=22,
            color=GREEN_C,
        ).to_edge(DOWN, buff=0.4)
        self.play(Write(constraint))
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])


# ============================================================================
# Scene 4 — Light Clock Animation
# ============================================================================


class LightClockAnimation(Scene):
    """Bouncing photon between two mirrors; Doppler-dilated tick for moving clock."""

    def construct(self):
        section_label = Text("The Light Clock", font_size=36, weight=BOLD).to_edge(UP)
        self.play(Write(section_label))
        self.wait(0.5)

        # ---- Stationary clock (left side) ----
        mirror_top_left = Line(LEFT * 1.5, RIGHT * 1.5, color=WHITE).shift(
            LEFT * 2.8 + UP * 1.5
        )
        mirror_bot_left = Line(LEFT * 1.5, RIGHT * 1.5, color=WHITE).shift(
            LEFT * 2.8 + DOWN * 1.5
        )
        label_stationary = Text("Stationary", font_size=22, color=GREY_B).next_to(
            mirror_top_left, UP, buff=0.2
        )

        # ---- Moving clock (right side) ----
        mirror_top_right = Line(LEFT * 1.5, RIGHT * 1.5, color=BLUE_C).shift(
            RIGHT * 2.8 + UP * 1.5
        )
        mirror_bot_right = Line(LEFT * 1.5, RIGHT * 1.5, color=BLUE_C).shift(
            RIGHT * 2.8 + DOWN * 1.5
        )
        label_moving = Text("Moving (v = 0.6c)", font_size=22, color=BLUE_C).next_to(
            mirror_top_right, UP, buff=0.2
        )

        self.play(
            Create(mirror_top_left),
            Create(mirror_bot_left),
            Write(label_stationary),
            Create(mirror_top_right),
            Create(mirror_bot_right),
            Write(label_moving),
        )
        self.wait(0.5)

        # ---- Photon for stationary clock ----
        photon_stat = Dot(color=YELLOW, radius=0.08).move_to(
            mirror_bot_left.get_center()
        )
        self.add(photon_stat)

        # ---- Photon for moving clock (diagonal path) ----
        photon_move = Dot(color=YELLOW, radius=0.08).move_to(
            mirror_bot_right.get_center()
        )
        self.add(photon_move)

        # Animate 3 bounces for each clock
        # Stationary: straight vertical; moving: diagonal (longer path = dilated time)
        stat_top = mirror_top_left.get_center()
        stat_bot = mirror_bot_left.get_center()

        # Moving clock — diagonal endpoints offset by 0.8 units horizontally per bounce
        move_bot = mirror_bot_right.get_center()
        move_top_diag = mirror_top_right.get_center() + RIGHT * 0.8
        move_bot_diag2 = mirror_bot_right.get_center() + RIGHT * 1.6

        # γ for β=0.6 is 1.25  →  moving clock ticks 1.25× slower
        stat_time = 0.8
        move_time = stat_time * 1.25

        # Tick counter labels
        stat_ticks = Integer(0, color=YELLOW).next_to(mirror_bot_left, DOWN, buff=0.3)
        move_ticks = Integer(0, color=YELLOW).next_to(mirror_bot_right, DOWN, buff=0.3)
        tick_label = Text("ticks", font_size=20, color=GREY_B)
        stat_tick_label = tick_label.copy().next_to(stat_ticks, RIGHT, buff=0.1)
        move_tick_label = tick_label.copy().next_to(move_ticks, RIGHT, buff=0.1)
        self.add(stat_ticks, stat_tick_label, move_ticks, move_tick_label)

        for bounce in range(3):
            # Stationary photon bounces straight up and back
            self.play(
                photon_stat.animate.move_to(stat_top),
                run_time=stat_time,
                rate_func=linear,
            )
            self.play(
                photon_stat.animate.move_to(stat_bot),
                run_time=stat_time,
                rate_func=linear,
            )
            stat_ticks.set_value(bounce + 1)

        # Moving photon bounces along diagonal (slower per tick)
        for i, dest in enumerate(
            [move_top_diag, move_bot_diag2, move_top_diag + RIGHT * 1.6]
        ):
            self.play(
                photon_move.animate.move_to(dest),
                run_time=move_time,
                rate_func=linear,
            )
            move_ticks.set_value(i + 1)

        self.wait(0.5)

        # Constraint annotation
        arrow = Arrow(
            stat_ticks.get_top() + UP * 0.3,
            move_ticks.get_top() + UP * 0.3,
            color=RED,
            buff=0.1,
        )
        constraint = Text(
            "Same coordinate time → fewer ticks in moving clock  (Δt' < Δt)",
            font_size=22,
            color=RED,
        ).to_edge(DOWN, buff=0.4)
        self.play(Create(arrow), Write(constraint))
        self.wait(3)

        self.play(*[FadeOut(m) for m in self.mobjects])


# ============================================================================
# Scene 5 — Conclusion
# ============================================================================


class TimeDilationConclusion(Scene):
    """Summary of key takeaways from time dilation."""

    def construct(self):
        title = Text("Key Takeaways", font_size=44, weight=BOLD).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        points = [
            r"\beta = v/c \quad \text{— fraction of light speed}",
            r"\gamma = \frac{1}{\sqrt{1-\beta^2}} \geq 1 \quad \text{— Lorentz factor}",
            r"\Delta t' = \gamma \, \Delta t \quad \text{— moving clocks run slower}",
            r"\text{At } \beta = 0.6,\; \gamma = 1.25 \quad \text{(25\% slower)}",
            r"\text{As } \beta \to 1,\; \gamma \to \infty \quad \text{(time stops)}",
        ]

        bullets = VGroup()
        for p in points:
            eq = MathTex(p, font_size=30)
            bullets.add(eq)
        bullets.arrange(DOWN, aligned_edge=LEFT, buff=0.45).shift(DOWN * 0.3)

        for bullet in bullets:
            self.play(FadeIn(bullet, shift=RIGHT * 0.3), run_time=0.7)
            self.wait(0.4)

        # Highlight the core constraint
        constraint_box = SurroundingRectangle(bullets[2], color=YELLOW, buff=0.15)
        constraint_note = Text(
            "Constraint: γ ≥ 1  →  time only slows, never reverses",
            font_size=22,
            color=YELLOW,
        ).to_edge(DOWN, buff=0.5)
        self.play(Create(constraint_box), Write(constraint_note))
        self.wait(3)

        # Fade to black
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.5)

        final = Text("ViviDoc — Interactive Educational Documents", font_size=26, color=GREY_C)
        self.play(FadeIn(final))
        self.wait(2)
        self.play(FadeOut(final))


# ============================================================================
# Composite scene — renders all 5 as one continuous video
# ============================================================================


class TimeDilationDoc(Scene):
    """All five scenes concatenated into a single continuous video."""

    def construct(self):
        for SceneClass in [
            TimeDilationIntro,
            LorentzFactorDerivation,
            LorentzFactorCurve,
            LightClockAnimation,
            TimeDilationConclusion,
        ]:
            instance = SceneClass()
            instance.camera = self.camera  # share the camera
            instance.renderer = self.renderer  # share the renderer
            instance.construct()

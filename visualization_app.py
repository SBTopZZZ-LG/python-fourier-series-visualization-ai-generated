# visualization_app.py

import sys
import pygame
import math
from constants import Constants
from input_box import InputBox, ColorInput
from button import Button
from checkbox import CheckBox

class VisualizationApp:
    def __init__(self, screen):
        self.screen = screen
        self.mode = Constants.INPUT_MODE
        self.lengths = [150, 50]  # Starting with 2 lines
        self.speeds = [0.05, -0.15]
        self.input_boxes = []  # List to hold tuples: ("label", surface, rect) or ("input", InputBox, None)
        self.joints = []  # List to hold joint dictionaries
        self.buttons = []
        self.trace_points = []
        self.joint_traces = []  # List to store the trace points of each joint
        self.paused = False
        self.hidden = False  # Flag to track visibility of lines, joints, and texts
        self.speed_multiplier = 1.0  # Initial speed multiplier
        self.min_speed_multiplier = 0.1  # Hard limit for slowing down
        self.speed_factor = 1.1  # Factor by which speed is increased/decreased
        self.time = 0  # Initialize time variable
        self.max_angular_increment = 0.1  # Maximum angular increment per sub-step (in radians)
        self.initialize_input_screen()

    def initialize_input_screen(self):
        self.input_boxes = []
        self.joints = []
        self.buttons = []

        # Define layout parameters for centering and spacing
        start_y = 50  # Starting Y position for "Start Visualization" button
        spacing_y = 60  # Vertical spacing between rows

        # Add 'Start Visualization' button at the top
        start_button = Button(
            x=Constants.WIDTH // 2 - 100,  # Center horizontally
            y=start_y,
            w=200,
            h=50,
            text="Start Visualization",
            callback=self.start_visualization,
            color=Constants.GREEN,
            hover_color=(0, 200, 0)
        )
        self.buttons.append(start_button)

        # Add 'Add Line' and 'Remove Line' buttons below the start button
        buttons_y = start_y + 60  # Position below the start button
        add_button = Button(
            x=Constants.WIDTH // 2 - 220,  # Position to the left
            y=buttons_y,
            w=120,
            h=40,
            text="Add Line",
            callback=self.add_line
        )
        remove_button = Button(
            x=Constants.WIDTH // 2 + 100,  # Position to the right
            y=buttons_y,
            w=120,
            h=40,
            text="Remove Line",
            callback=self.remove_line
        )
        self.buttons.extend([add_button, remove_button])

        # Define input fields starting position
        input_start_y = buttons_y + 60  # Start below the buttons
        input_spacing_y = 60  # Space between each line's input fields

        # Add input boxes for existing lines
        for i in range(len(self.lengths)):
            y_pos = input_start_y + i * input_spacing_y

            # Line label
            line_label = pygame.font.SysFont(None, Constants.FONT_SIZE).render(f"Line {i+1}:", True, Constants.WHITE)
            line_label_rect = line_label.get_rect()
            line_label_rect.topleft = (Constants.WIDTH // 2 - 300, y_pos + 8)
            self.input_boxes.append(("label", line_label, line_label_rect))

            # Length input box
            length_box = InputBox(
                x=Constants.WIDTH // 2 - 200,
                y=y_pos,
                w=100,
                h=32,
                placeholder='Length',
                unit='pixels'
            )
            length_box.text = str(self.lengths[i])
            length_box.txt_surface = length_box.font.render(length_box.text, True, Constants.WHITE)
            self.input_boxes.append(("input", length_box, None))

            # Speed input box (Adjusted X-coordinate to fix overlapping)
            speed_box = InputBox(
                x=Constants.WIDTH // 2,
                y=y_pos,
                w=100,
                h=32,
                placeholder='Speed',
                unit='rad/frame'
            )
            speed_box.text = str(self.speeds[i])
            speed_box.txt_surface = speed_box.font.render(speed_box.text, True, Constants.WHITE)
            self.input_boxes.append(("input", speed_box, None))

            # If not the first line, add a joint above this line
            if i > 0:
                joint_y = y_pos - input_spacing_y // 2
                joint_checkbox = CheckBox(
                    x=Constants.WIDTH // 2 - 300,
                    y=joint_y,
                    size=20,
                    checked=False
                )
                joint_color_input = ColorInput(
                    x=Constants.WIDTH // 2 - 250,
                    y=joint_y,
                    w=100,
                    h=32,
                    placeholder='#FF0000',  # Default to red for visibility
                    unit=''
                )
                self.joints.append({
                    'checkbox': joint_checkbox,
                    'color_input': joint_color_input
                })
                self.input_boxes.append(("joint_checkbox", joint_checkbox, None))
                self.input_boxes.append(("joint_color", joint_color_input, None))

        # Initialize joint_traces
        self.joint_traces = [[] for _ in self.joints]

    def add_line(self):
        new_length = 50
        new_speed = 0.02

        # Define layout parameters
        input_start_y = 50 + 60 + 60  # start_y + buttons_y + spacing
        input_spacing_y = 60  # Space between each line's input fields
        i = len(self.lengths)  # New line index

        y_pos = 170 + i * input_spacing_y  # 50(start_y) +60(buttons_y)+60(first line) =170

        # Line label
        line_label = pygame.font.SysFont(None, Constants.FONT_SIZE).render(f"Line {i+1}:", True, Constants.WHITE)
        line_label_rect = line_label.get_rect()
        line_label_rect.topleft = (Constants.WIDTH // 2 - 300, y_pos + 8)
        self.input_boxes.append(("label", line_label, line_label_rect))

        # Length input box
        length_box = InputBox(
            x=Constants.WIDTH // 2 - 200,
            y=y_pos,
            w=100,
            h=32,
            placeholder='Length',
            unit='pixels'
        )
        length_box.text = str(new_length)
        length_box.txt_surface = length_box.font.render(length_box.text, True, Constants.WHITE)
        self.input_boxes.append(("input", length_box, None))

        # Speed input box (Adjusted X-coordinate to fix overlapping)
        speed_box = InputBox(
            x=Constants.WIDTH // 2,
            y=y_pos,
            w=100,
            h=32,
            placeholder='Speed',
            unit='rad/frame'
        )
        speed_box.text = str(new_speed)
        speed_box.txt_surface = speed_box.font.render(speed_box.text, True, Constants.WHITE)
        self.input_boxes.append(("input", speed_box, None))

        # Add joint for the new line if it's not the first line
        if i > 0:
            joint_y = y_pos - input_spacing_y // 2
            joint_checkbox = CheckBox(
                x=Constants.WIDTH // 2 - 300,
                y=joint_y,
                size=20,
                checked=False
            )
            joint_color_input = ColorInput(
                x=Constants.WIDTH // 2 - 250,
                y=joint_y,
                w=100,
                h=32,
                placeholder='#FF0000',  # Default to red for visibility
                unit=''
            )
            self.joints.append({
                'checkbox': joint_checkbox,
                'color_input': joint_color_input
            })
            self.input_boxes.append(("joint_checkbox", joint_checkbox, None))
            self.input_boxes.append(("joint_color", joint_color_input, None))

            # Initialize a new joint trace
            self.joint_traces.append([])

        # Update lengths and speeds lists
        self.lengths.append(new_length)
        self.speeds.append(new_speed)

    def remove_line(self):
        if len(self.lengths) > 0:
            # Remove the last set of input boxes (label, length, speed)
            for _ in range(3):
                if self.input_boxes:
                    self.input_boxes.pop()
            # If there is a joint above this line, remove it
            if len(self.joints) > 0:
                # Remove joint checkbox and color input from input_boxes
                for _ in range(2):
                    if self.input_boxes:
                        self.input_boxes.pop()
                # Remove the joint and its trace
                self.joints.pop()
                if self.joint_traces:
                    self.joint_traces.pop()
            # Remove from lengths and speeds
            self.lengths.pop()
            self.speeds.pop()
        else:
            print("No more lines to remove.")

    def start_visualization(self):
        # Gather inputs
        lengths = []
        speeds = []
        for item in self.input_boxes:
            if item[0] == "input":
                box = item[1]
                if 'pixels' in box.unit:
                    length = box.get_value()
                    if length is None or length <= 0:
                        print("Invalid length input detected. Please enter valid positive numbers.")
                        return
                    lengths.append(length)
                elif 'rad/frame' in box.unit:
                    speed = box.get_value()
                    if speed is None:
                        print("Invalid speed input detected. Please enter valid numbers.")
                        return
                    speeds.append(speed)
        if not lengths or not speeds or len(lengths) != len(speeds):
            print("Mismatch in the number of lengths and speeds. Please check your inputs.")
            return
        self.lengths = lengths
        self.speeds = speeds
        self.trace_points = []
        self.joint_traces = [[] for _ in self.joints]  # Initialize joint traces
        self.paused = False
        self.hidden = False  # Reset hidden state when starting visualization
        self.speed_multiplier = 1.0  # Reset speed multiplier
        self.time = 0  # Reset time when starting a new visualization
        self.mode = Constants.VISUALIZE_MODE
        print("Switched to VISUALIZE_MODE")

    def handle_input_events(self, event):
        for item in self.input_boxes:
            if item[0] == "input":
                box = item[1]
                box.handle_event(event)
            elif item[0] == "joint_checkbox":
                checkbox = item[1]
                checkbox.handle_event(event)
            elif item[0] == "joint_color":
                color_input = item[1]
                color_input.handle_event(event)
        for button in self.buttons:
            button.handle_event(event)

    def draw_input_screen(self):
        self.screen.fill(Constants.BLACK)
        # Title
        title_font = pygame.font.SysFont(None, Constants.BUTTON_FONT_SIZE)
        title_surf = title_font.render("Configure Rotating Lines", True, Constants.WHITE)
        self.screen.blit(title_surf, (Constants.WIDTH // 2 - title_surf.get_width() // 2, 10))

        # Draw input boxes, labels, checkboxes, and color inputs
        for item in self.input_boxes:
            if item[0] == "label":
                label_surf, label_rect = item[1], item[2]
                self.screen.blit(label_surf, label_rect)
            elif item[0] == "input":
                box = item[1]
                if isinstance(box, InputBox):
                    box.draw(self.screen)
                else:
                    print(f"Error: Expected InputBox instance, got {type(box)}")
            elif item[0] == "joint_checkbox":
                checkbox = item[1]
                checkbox.draw(self.screen)
            elif item[0] == "joint_color":
                color_input = item[1]
                color_input.draw(self.screen)

        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)

    def handle_visualize_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.paused = not self.paused
                state = "Paused" if self.paused else "Resumed"
                print(state)
            elif event.key == pygame.K_ESCAPE:
                # Abort visualization and return to input mode
                self.mode = Constants.INPUT_MODE
                self.initialize_input_screen()
                print("Aborted visualization. Returned to INPUT_MODE.")
            elif event.key == pygame.K_COMMA:  # '<' key (comma key on some keyboards)
                self.decrease_speed()
            elif event.key == pygame.K_PERIOD:  # '>' key (period key on some keyboards)
                self.increase_speed()
            elif event.key == pygame.K_h:  # 'H' key to hide/show lines, joints, and texts
                self.toggle_hide()

    def decrease_speed(self):
        new_multiplier = self.speed_multiplier / self.speed_factor
        if new_multiplier >= self.min_speed_multiplier:
            self.speed_multiplier = new_multiplier
            print(f"Speed decreased. Current multiplier: {self.speed_multiplier:.2f}")
        else:
            self.speed_multiplier = self.min_speed_multiplier
            print(f"Speed is at minimum multiplier: {self.speed_multiplier:.2f}")

    def increase_speed(self):
        self.speed_multiplier *= self.speed_factor
        print(f"Speed increased. Current multiplier: {self.speed_multiplier:.2f}")

    def toggle_hide(self):
        self.hidden = not self.hidden
        state = "hidden" if self.hidden else "visible"
        print(f"Components are now {state}.")

    def draw_visualization_screen(self):
        # Fill the screen with black to clear previous drawings
        self.screen.fill(Constants.BLACK)

        # Draw the traces of the joints
        for idx, joint_trace in enumerate(self.joint_traces):
            if len(joint_trace) > 1:
                color = self.joints[idx]['color_input'].get_color()
                if color is None:
                    color = Constants.WHITE  # Default color if invalid
                pygame.draw.lines(self.screen, color, False, joint_trace, 2)  # Thickness 2

        # Draw the trace of the last endpoint
        if len(self.trace_points) > 1:
            pygame.draw.lines(self.screen, Constants.DRAW_COLOR, False, self.trace_points, 1)

        # Calculate positions
        positions = [Constants.CENTER]
        for i in range(len(self.lengths)):
            angle = self.speeds[i] * self.time  # Calculate angle based on time
            length = self.lengths[i]
            x = positions[i][0] + length * math.cos(angle)
            y = positions[i][1] + length * math.sin(angle)
            positions.append((x, y))

        if not self.hidden:
            # Draw the lines and joints only if not hidden
            for i in range(len(self.lengths)):
                pygame.draw.line(self.screen, Constants.WHITE, positions[i], positions[i + 1], 2)
                if i < len(self.lengths) - 1:
                    pygame.draw.circle(self.screen, Constants.LIGHT_BLUE, (int(positions[i + 1][0]), int(positions[i + 1][1])), 5)

            # Draw faint control label at bottom right
            control_text = "Press P to pause/resume, Escape to abort, < to decrease speed, > to increase speed, H to hide/show components"
            control_font = pygame.font.SysFont(None, Constants.FONT_SIZE)
            control_surf = control_font.render(control_text, True, Constants.FAINT_WHITE)
            self.screen.blit(control_surf, (Constants.WIDTH - control_surf.get_width() - 10, Constants.HEIGHT - control_surf.get_height() - 10))

            # If paused, display 'Paused' text
            if self.paused:
                paused_font = pygame.font.SysFont(None, Constants.BUTTON_FONT_SIZE)
                paused_surf = paused_font.render("Paused", True, Constants.RED)
                self.screen.blit(paused_surf, (Constants.WIDTH // 2 - paused_surf.get_width() // 2, 10))

    def update_visualization(self):
        if not self.paused:
            # Calculate total time to advance this frame
            total_delta_time = self.speed_multiplier
            remaining_time = total_delta_time

            # Determine the maximum allowable time step
            max_speed = max(abs(speed) for speed in self.speeds)
            if max_speed != 0:
                max_delta_time = self.max_angular_increment / max_speed
            else:
                max_delta_time = total_delta_time  # No need to sub-step if all speeds are zero

            # Subdivide the time step if necessary
            while remaining_time > 0:
                delta_time = min(remaining_time, max_delta_time)
                self.time += delta_time
                remaining_time -= delta_time

                # Calculate positions for this sub-step
                positions = [Constants.CENTER]
                for i in range(len(self.lengths)):
                    angle = self.speeds[i] * self.time
                    length = self.lengths[i]
                    x = positions[i][0] + length * math.cos(angle)
                    y = positions[i][1] + length * math.sin(angle)
                    positions.append((x, y))

                # Store the position of the last endpoint
                self.trace_points.append(positions[-1])

                # Store the positions of the enabled joints
                for idx, joint in enumerate(self.joints):
                    if joint['checkbox'].is_checked():
                        # The position of the joint is positions[idx + 1]
                        self.joint_traces[idx].append(positions[idx + 1])

    def run(self, clock):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.mode == Constants.INPUT_MODE:
                    self.handle_input_events(event)
                elif self.mode == Constants.VISUALIZE_MODE:
                    self.handle_visualize_events(event)

            if self.mode == Constants.INPUT_MODE:
                self.draw_input_screen()
            elif self.mode == Constants.VISUALIZE_MODE:
                self.update_visualization()
                self.draw_visualization_screen()

            pygame.display.flip()
            clock.tick(Constants.FPS)

import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
CENTER = (WIDTH // 2, HEIGHT // 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotating Lines Visualization")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
DRAW_COLOR = (200, 200, 200)  # Slightly darker than white
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FAINT_WHITE = (200, 200, 200)  # For faint labels

# Fonts
FONT = pygame.font.SysFont(None, 24)
BUTTON_FONT = pygame.font.SysFont(None, 28)

# Frame rate
FPS = 60
clock = pygame.time.Clock()

# Define InputBox class
class InputBox:
    def __init__(self, x, y, w, h, placeholder='', unit=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = ''
        self.placeholder = placeholder
        self.unit = unit
        self.txt_surface = FONT.render(self.text if self.text else self.placeholder, True, WHITE if self.text else GRAY)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            self.active = self.rect.collidepoint(event.pos)
            self.color = LIGHT_BLUE if self.active else GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = GRAY
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 10 and event.unicode.isprintable():
                        self.text += event.unicode
                # Re-render the text.
                display_text = self.text if self.text else self.placeholder
                self.txt_surface = FONT.render(display_text, True, WHITE if self.text else GRAY)

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # Blit the unit label
        if self.unit:
            unit_surf = FONT.render(self.unit, True, WHITE)
            screen.blit(unit_surf, (self.rect.x + self.rect.width + 10, self.rect.y + 8))

    def get_value(self):
        try:
            return float(self.text)
        except ValueError:
            return None

    def clear(self):
        self.text = ''
        self.txt_surface = FONT.render(self.placeholder, True, GRAY)

# Define Button class
class Button:
    def __init__(self, x, y, w, h, text, callback, color=GRAY, hover_color=LIGHT_BLUE):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.callback = callback
        self.txt_surface = BUTTON_FONT.render(text, True, BLACK)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        # Center the text
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)

# Application States
INPUT_MODE = 'input'
VISUALIZE_MODE = 'visualize'

class VisualizationApp:
    def __init__(self):
        self.mode = INPUT_MODE
        self.lengths = [100, 80, 60, 40]
        self.speeds = [0.02, 0.04, 0.06, 0.08]
        self.input_boxes = []  # List to hold tuples: ("label", surface, rect) or ("input", InputBox, None)
        self.buttons = []
        self.trace_points = []
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
        self.buttons = []

        # Define layout parameters for centering and spacing
        start_y = 50  # Starting Y position for "Start Visualization" button
        spacing_y = 60  # Vertical spacing between rows

        # Add 'Start Visualization' button at the top
        start_button = Button(
            x=WIDTH // 2 - 100,  # Center horizontally
            y=start_y,
            w=200,
            h=50,
            text="Start Visualization",
            callback=self.start_visualization,
            color=GREEN,
            hover_color=(0, 200, 0)
        )
        self.buttons.append(start_button)

        # Add 'Add Line' and 'Remove Line' buttons below the start button
        buttons_y = start_y + 60  # Position below the start button
        add_button = Button(
            x=WIDTH // 2 - 220,  # Position to the left
            y=buttons_y,
            w=120,
            h=40,
            text="Add Line",
            callback=self.add_line
        )
        remove_button = Button(
            x=WIDTH // 2 + 100,  # Position to the right
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
            line_label = FONT.render(f"Line {i+1}:", True, WHITE)
            line_label_rect = line_label.get_rect()
            line_label_rect.topleft = (WIDTH // 2 - 300, y_pos + 8)
            self.input_boxes.append(("label", line_label, line_label_rect))

            # Length input box
            length_box = InputBox(
                x=WIDTH // 2 - 200,
                y=y_pos,
                w=100,
                h=32,
                placeholder='Length',
                unit='pixels'
            )
            length_box.text = str(self.lengths[i])
            length_box.txt_surface = FONT.render(length_box.text, True, WHITE)
            self.input_boxes.append(("input", length_box, None))

            # Speed input box (Adjusted X-coordinate to fix overlapping)
            speed_box = InputBox(
                x=WIDTH // 2,
                y=y_pos,
                w=100,
                h=32,
                placeholder='Speed',
                unit='rad/frame'
            )
            speed_box.text = str(self.speeds[i])
            speed_box.txt_surface = FONT.render(speed_box.text, True, WHITE)
            self.input_boxes.append(("input", speed_box, None))

    def add_line(self):
        new_length = 50
        new_speed = 0.02

        # Define layout parameters
        input_start_y = 50 + 60 + 60  # start_y + buttons_y + spacing
        input_spacing_y = 60  # Space between each line's input fields
        i = len(self.lengths)  # New line index

        y_pos = 170 + i * input_spacing_y  # 50(start_y) +60(buttons_y)+60(first line) =170

        # Line label
        line_label = FONT.render(f"Line {i+1}:", True, WHITE)
        line_label_rect = line_label.get_rect()
        line_label_rect.topleft = (WIDTH // 2 - 300, y_pos + 8)
        self.input_boxes.append(("label", line_label, line_label_rect))

        # Length input box
        length_box = InputBox(
            x=WIDTH // 2 - 200,
            y=y_pos,
            w=100,
            h=32,
            placeholder='Length',
            unit='pixels'
        )
        length_box.text = str(new_length)
        length_box.txt_surface = FONT.render(length_box.text, True, WHITE)
        self.input_boxes.append(("input", length_box, None))

        # Speed input box (Adjusted X-coordinate to fix overlapping)
        speed_box = InputBox(
            x=WIDTH // 2,
            y=y_pos,
            w=100,
            h=32,
            placeholder='Speed',
            unit='rad/frame'
        )
        speed_box.text = str(new_speed)
        speed_box.txt_surface = FONT.render(speed_box.text, True, WHITE)
        self.input_boxes.append(("input", speed_box, None))

        # Update lengths and speeds lists
        self.lengths.append(new_length)
        self.speeds.append(new_speed)

    def remove_line(self):
        if len(self.lengths) > 0:
            # Remove the last set of input boxes (label, length, speed)
            for _ in range(3):
                if self.input_boxes:
                    self.input_boxes.pop()
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
                    if length is None:
                        print("Invalid length input detected. Please enter valid numbers.")
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
        self.paused = False
        self.hidden = False  # Reset hidden state when starting visualization
        self.speed_multiplier = 1.0  # Reset speed multiplier
        self.time = 0  # Reset time when starting a new visualization
        self.mode = VISUALIZE_MODE

    def handle_input_events(self, event):
        for item in self.input_boxes:
            if item[0] == "input":
                box = item[1]
                box.handle_event(event)
        for button in self.buttons:
            button.handle_event(event)

    def draw_input_screen(self):
        screen.fill(BLACK)
        # Title
        title_surf = BUTTON_FONT.render("Configure Rotating Lines", True, WHITE)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 10))

        # Draw input boxes and labels
        for item in self.input_boxes:
            if item[0] == "label":
                label_surf, label_rect = item[1], item[2]
                screen.blit(label_surf, label_rect)
            elif item[0] == "input":
                box = item[1]
                if isinstance(box, InputBox):
                    box.draw(screen)
                else:
                    print(f"Error: Expected InputBox instance, got {type(box)}")

        # Draw buttons
        for button in self.buttons:
            button.draw(screen)

    def handle_visualize_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.paused = not self.paused
            elif event.key == pygame.K_ESCAPE:
                # Abort visualization and return to input mode
                self.mode = INPUT_MODE
                self.initialize_input_screen()
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

    def visualize_mode_setup(self):
        # No GUI elements to setup in visualize mode
        pass

    def draw_visualization_screen(self):
        # Draw the trace
        if len(self.trace_points) > 1:
            pygame.draw.lines(screen, DRAW_COLOR, False, self.trace_points, 1)

        # Calculate positions
        positions = [CENTER]
        for i in range(len(self.lengths)):
            angle = self.speeds[i] * self.time  # Calculate angle based on time
            length = self.lengths[i]
            x = positions[i][0] + length * math.cos(angle)
            y = positions[i][1] + length * math.sin(angle)
            positions.append((x, y))

        if not self.hidden:
            # Draw the lines and joints only if not hidden
            for i in range(len(self.lengths)):
                pygame.draw.line(screen, WHITE, positions[i], positions[i + 1], 2)
                if i < len(self.lengths) - 1:
                    pygame.draw.circle(screen, LIGHT_BLUE, (int(positions[i + 1][0]), int(positions[i + 1][1])), 5)

            # Draw faint control label at bottom right
            control_text = "Press P to pause/resume, Escape to abort, < to decrease speed, > to increase speed, H to hide/show components"
            control_surf = FONT.render(control_text, True, FAINT_WHITE)
            screen.blit(control_surf, (WIDTH - control_surf.get_width() - 10, HEIGHT - control_surf.get_height() - 10))

            # If paused, display 'Paused' text
            if self.paused:
                paused_surf = BUTTON_FONT.render("Paused", True, RED)
                screen.blit(paused_surf, (WIDTH // 2 - paused_surf.get_width() // 2, 10))

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
                positions = [CENTER]
                for i in range(len(self.lengths)):
                    angle = self.speeds[i] * self.time
                    length = self.lengths[i]
                    x = positions[i][0] + length * math.cos(angle)
                    y = positions[i][1] + length * math.sin(angle)
                    positions.append((x, y))

                # Store the position of the last endpoint
                self.trace_points.append(positions[-1])

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.mode == INPUT_MODE:
                    self.handle_input_events(event)
                elif self.mode == VISUALIZE_MODE:
                    self.handle_visualize_events(event)

            if self.mode == INPUT_MODE:
                self.draw_input_screen()
            elif self.mode == VISUALIZE_MODE:
                self.update_visualization()
                screen.fill(BLACK)
                self.draw_visualization_screen()

            pygame.display.flip()
            clock.tick(FPS)

# Create and run the application
if __name__ == "__main__":
    app = VisualizationApp()
    app.run()

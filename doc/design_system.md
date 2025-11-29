# Personal Vibe CEO - Design System

## Overview
This design system is inspired by Apple's Human Interface Guidelines, focusing on clarity, deference, and depth. It utilizes a neutral color palette, system typography, and glassmorphism to create a modern, sleek, and professional aesthetic.

## Core Principles
- **Clean & Minimal**: Content comes first. Unnecessary decorations are removed.
- **Glassmorphism**: Translucent materials (`backdrop-filter`) are used to establish hierarchy and depth.
- **Fluid Interactions**: Smooth transitions and subtle animations enhance the user experience.

## Typography
We use the system font stack to ensure the app feels native on every device.

```css
font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
```

## Color Palette

### Light Mode
| Token                | Hex                        | Usage                             |
| -------------------- | -------------------------- | --------------------------------- |
| `--background`       | `#F5F5F7`                  | Main app background (Light Gray)  |
| `--foreground`       | `#1D1D1F`                  | Primary text color (Almost Black) |
| `--card-background`  | `rgba(255, 255, 255, 0.7)` | Glass cards                       |
| `--primary`          | `#0071E3`                  | Primary actions (Apple Blue)      |
| `--muted-foreground` | `#86868B`                  | Secondary text                    |

### Dark Mode
| Token                | Hex                     | Usage                            |
| -------------------- | ----------------------- | -------------------------------- |
| `--background`       | `#000000`               | Main app background (Pure Black) |
| `--foreground`       | `#F5F5F7`               | Primary text color (Off White)   |
| `--card-background`  | `rgba(28, 28, 30, 0.7)` | Glass cards                      |
| `--primary`          | `#0A84FF`               | Primary actions (Light Blue)     |
| `--muted-foreground` | `#86868B`               | Secondary text                   |

## UI Utilities

### Glassmorphism
Use the `.glass` or `.glass-card` classes to apply the frosted glass effect.

```css
.glass-card {
  background: var(--card-background);
  backdrop-filter: blur(20px);
  border: 1px solid var(--card-border);
}
```

### Shadows & Radius
- **Border Radius**: Generous rounding (`1.5rem` to `2rem`) for cards and buttons.
- **Shadows**: Soft, diffused shadows to lift elements off the background.

## Components

### Buttons
- **Primary**: Pill-shaped, solid primary color, white text.
- **Secondary/Ghost**: Transparent or subtle background, primary colored text.

### Inputs
- **Text Fields**: Minimalist, often with a glass background or simple bottom border.
- **Message Input**: Floating pill shape with internal submit button.

### Chat Bubbles
- **User**: Solid primary color, rounded corners (iMessage style).
- **Agent**: Glassmorphic background, text color adapts to theme.

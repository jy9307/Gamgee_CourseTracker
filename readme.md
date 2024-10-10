# Gamgee - Assistant for for teachers

# Patch Notes

## v0.4 - 2024-10-06
    - Add a "manual mode" layout for users who want to input their account information manually, including fields for username and password. The entire window will be divided into two sections: "manual mode" and "automation mode."
    - Add a "speed control" button on the progress dialog, allowing users to select their desired playback speed. This feature should offer a range of speed options (e.g., 0.5x, 1x, 1.5x, 2x).
    - Improve the GUI of the progress dialog for better visibility.

## v0.3 - 2024-09-26
- Add an 'automated mute' button on progress dialog for users to select whether the lecture should be muted.
- Add a 'hide window' button and a 'restore window' button on progress dialog for users to select whether the window should be displayed.

## v0.21 - 2024-09-25
- Resolve the issue where it doesn't work in a specific lecture. ex) '평등한 일상, 폭력예방교육'

## v0.2 - 2024-09-13
- Made notification of automation disappeared.
- Added loop-passer(continue) for quiz page in main process loop so error don't raise.
- Modified the code that searches for the element of 'video player control bar' to wait for 3 seconds until the element is found.
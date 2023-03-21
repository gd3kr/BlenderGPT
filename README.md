# GPT-4 Blender Assistant

This Blender extension allows you to generate Blender Python code by providing a natural language command. The extension utilizes OpenAI's GPT-4 model to generate the code and perform various tasks within Blender.

## Features

- Generate Blender Python code from natural language commands
- Integrated with Blender's UI for easy usage
- Supports Blender version 2.82.0 and above

## Installation

1. Download the latest release from GitHub
2. Open Blender, go to `Edit > Preferences > Add-ons > Install`
3. Select the downloaded ZIP file and click `Install Add-on`
4. Enable the add-on by checking the checkbox next to `GPT-4 Blender Assistant`

## Usage

1. In the 3D View, open the sidebar (press `N` if not visible) and locate the `GPT-4 Assistant` tab
2. Type a natural language command in the input field, e.g., "create a cube at the origin"
3. Click the `Execute` button to generate and execute the Blender Python code

## Requirements

- Blender 2.82.0 or later
- OpenAI API key (set as an environment variable `OPENAI_API_KEY`)

## Limitations

- The generated code might not always be correct. In that case, run it again lmao.
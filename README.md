# BlenderGPT
![Header](https://user-images.githubusercontent.com/63528145/227160213-6862cd5e-b31f-43ea-a5e5-6cc340a95617.png)






Blender can be controlled using program scripts written in Python. Recent Large Language Models like OpenAI's GPT-4 can generate these Python scripts from simple English and execute them. This plugin provides an easy to use interface that integrates OpenAI's GPT-4/GPT-3.5 right in the UI, allowing you to use natural language commands to control Blender.

# Note

Access to GPT-4 in this addon can ONLY be obtained through the OpenAI waitlist (https://openai.com/waitlist/gpt-4-api), which in turn grants your account access to this model via the API.


**GPT-4 access via the API is different from GPT-4 access via ChatGPT-Plus ($20/month subscription). This addon will only work with GPT-4 if you have been accepted into the waitlist (https://openai.com/waitlist/gpt-4-api) and have access to the API via your OpenAI API key**

## Installation

1. Clone this repository by clicking `Code > Download ZIP` on GitHub
2. Open Blender, go to `Edit > Preferences > Add-ons > Install`
3. Select the downloaded ZIP file and click `Install Add-on`
4. Enable the add-on by checking the checkbox next to `GPT-4 Blender Assistant`
5. Paste your OpenAI API key in the Addon preferences menu.
5. To view the code generations in realtime, go to `Window > Toggle System Console`

## Usage

1. In the 3D View, open the sidebar (press `N` if not visible) and locate the `GPT-4 Assistant` tab
2. Type a natural language command in the input field, e.g., "create a cube at the origin"
3. Click the `Execute` button to generate and execute the Blender Python code


## Requirements

- Blender 3.1 or later
- OpenAI API key (Accessible at https://platform.openai.com/account/api-keys)


## Demonstration
https://user-images.githubusercontent.com/63528145/227158577-d92c6e8d-df21-4461-a69b-9e7cde8c8dcf.mov

import sys
import os
import bpy
import bpy.props
import re

bl_info = {
    "name": "GPT-4 Blender Assistant",
    "blender": (2, 82, 0),
    "category": "Object",
    "author": "Aarya (@gd3kr)",
    "version": (2, 0, 0),
    "location": "3D View > UI > GPT-4 Blender Assistant",
    "description": "Generate Blender Python code using OpenAI's GPT-4 to perform various tasks.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
}

system_prompt = """You are an assistant made for the purposes of helping the user with Blender, the 3D software. 
- Respond with your answers in markdown (```). 
- Preferably import entire modules instead of bits. 
- Do not perform destructive operations on the meshes. 
- Do not use cap_ends. Do not do more than what is asked (setting up render settings, adding cameras, etc)
- Do not respond with anything that is not Python code.

Example:

user: create 10 cubes in random locations from -10 to 10
assistant:
```
import bpy
import random
bpy.ops.mesh.primitive_cube_add()

#how many cubes you want to add
count = 10

for c in range(0,count):
    x = random.randint(-10,10)
    y = random.randint(-10,10)
    z = random.randint(-10,10)
    bpy.ops.mesh.primitive_cube_add(location=(x,y,z))
```"""


# Add the 'libs' folder to the Python path
libs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
if libs_path not in sys.path:
    sys.path.append(libs_path)



import openai

def get_api_key(context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__name__].preferences
    return addon_prefs.api_key


def init_props():
    bpy.types.Scene.gpt4_chat_history = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.gpt4_chat_input = bpy.props.StringProperty(
        name="Message",
        description="Enter your message",
        default="",
    )
    bpy.types.Scene.gpt4_button_pressed = bpy.props.BoolProperty(default=False)
    bpy.types.PropertyGroup.type = bpy.props.StringProperty()
    bpy.types.PropertyGroup.content = bpy.props.StringProperty()

def clear_props():
    del bpy.types.Scene.gpt4_chat_history
    del bpy.types.Scene.gpt4_chat_input
    del bpy.types.Scene.gpt4_button_pressed

def generate_blender_code(prompt, chat_history):
    messages = [{"role": "system", "content": system_prompt}]
    for message in chat_history[-10:]:
        if message.type == "assistant":
            messages.append({"role": "assistant", "content": "```\n" + message.content + "\n```"})
        else:
            messages.append({"role": message.type.lower(), "content": message.content})

    # Add the current user message
    messages.append({"role": "user", "content": "Can you please write Blender code for me that accomplishes the following task: " + prompt + "? \n. Do not respond with anything that is not Python code. Do not provide explanations"})


    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            stream=True,
            max_tokens=1500,
        )
    except Exception as e: # Use GPT-3.5 if GPT-4 is not available
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
            max_tokens=1500,
        )

    try:
        collected_events = []
        completion_text = ''
        # iterate through the stream of events
        for event in response:
            if 'role' in event['choices'][0]['delta']:
                # skip
                continue
            if len(event['choices'][0]['delta']) == 0:
                # skip
                continue
            collected_events.append(event)  # save the event response
            event_text = event['choices'][0]['delta']['content']
            completion_text += event_text  # append the text
            print(completion_text, flush=True, end='\r')
        completion_text = re.findall(r'```(.*?)```', completion_text, re.DOTALL)[0]
        completion_text = re.sub(r'^python', '', completion_text, flags=re.MULTILINE)
        
        return completion_text
    except IndexError:
        return None

def split_area_to_text_editor(context):
    area = context.area
    for region in area.regions:
        if region.type == 'WINDOW':
            override = {'area': area, 'region': region}
            bpy.ops.screen.area_split(override, direction='VERTICAL', factor=0.5)
            break

    new_area = context.screen.areas[-1]
    new_area.type = 'TEXT_EDITOR'
    return new_area


class GPT4_OT_ShowCode(bpy.types.Operator):
    bl_idname = "gpt4.show_code"
    bl_label = "Show Code"
    bl_options = {'REGISTER', 'UNDO'}

    code: bpy.props.StringProperty(
        name="Code",
        description="The generated code",
        default="",
    )

    def execute(self, context):
        text_name = "GPT4_Generated_Code.py"
        text = bpy.data.texts.get(text_name)
        if text is None:
            text = bpy.data.texts.new(text_name)

        text.clear()
        text.write(self.code)

        text_editor_area = None
        for area in context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                text_editor_area = area
                break

        if text_editor_area is None:
            text_editor_area = split_area_to_text_editor(context)
        
        text_editor_area.spaces.active.text = text

        return {'FINISHED'}

class GPT4_PT_Panel(bpy.types.Panel):
    bl_label = "GPT-4 Blender Assistant"
    bl_idname = "GPT4_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GPT-4 Assistant'

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)

        column.label(text="Chat history:")
        box = column.box()
        for message in context.scene.gpt4_chat_history:
            if message.type == 'assistant':
                row = box.row()
                row.label(text="Assistant: ")
                show_code_op = row.operator("gpt4.show_code", text="Show Code")
                show_code_op.code = message.content
            else:
                box.label(text=f"User: {message.content}")

        column.separator()

        column.label(text="Enter your message:")
        column.prop(context.scene, "gpt4_chat_input", text="")
        button_label = "Please wait...(this might take some time)" if context.scene.gpt4_button_pressed else "Execute"
        row = column.row(align=True)
        row.operator("gpt4.send_message", text=button_label)
        row.operator("gpt4.clear_chat", text="Clear Chat")

        column.separator()

class GPT4_OT_ClearChat(bpy.types.Operator):
    bl_idname = "gpt4.clear_chat"
    bl_label = "Clear Chat"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gpt4_chat_history.clear()
        return {'FINISHED'}

class GPT4_OT_Execute(bpy.types.Operator):
    bl_idname = "gpt4.send_message"
    bl_label = "Send Message"
    bl_options = {'REGISTER', 'UNDO'}

    natural_language_input: bpy.props.StringProperty(
        name="Command",
        description="Enter the natural language command",
        default="",
    )

    def execute(self, context):
        openai.api_key = get_api_key(context)

        if not openai.api_key:
            self.report({'ERROR'}, "No API key detected. Please set the API key in the addon preferences.")
            return {'CANCELLED'}

        context.scene.gpt4_button_pressed = True
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        
        blender_code = generate_blender_code(context.scene.gpt4_chat_input, context.scene.gpt4_chat_history)

        message = context.scene.gpt4_chat_history.add()
        message.type = 'user'
        message.content = context.scene.gpt4_chat_input

        # Clear the chat input field
        context.scene.gpt4_chat_input = ""

    
        if blender_code:
            message = context.scene.gpt4_chat_history.add()
            message.type = 'assistant'
            message.content = blender_code

            global_namespace = globals().copy()
    
        try:
            exec(blender_code, global_namespace)
        except Exception as e:
            self.report({'ERROR'}, f"Error executing generated code: {e}")
            context.scene.gpt4_button_pressed = False
            return {'CANCELLED'}

        

        context.scene.gpt4_button_pressed = False
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(GPT4_OT_Execute.bl_idname)

class GPT4AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    api_key: bpy.props.StringProperty(
        name="API Key",
        description="Enter your OpenAI API Key",
        default="",
        subtype="PASSWORD",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "api_key")

def register():
    bpy.utils.register_class(GPT4AddonPreferences)
    bpy.utils.register_class(GPT4_OT_Execute)
    bpy.utils.register_class(GPT4_PT_Panel)
    bpy.utils.register_class(GPT4_OT_ClearChat)
    bpy.utils.register_class(GPT4_OT_ShowCode)

    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)
    init_props()


def unregister():
    bpy.utils.unregister_class(GPT4AddonPreferences)
    bpy.utils.unregister_class(GPT4_OT_Execute)
    bpy.utils.unregister_class(GPT4_PT_Panel)
    bpy.utils.unregister_class(GPT4_OT_ClearChat)
    bpy.utils.register_class(GPT4_OT_ShowCode)

    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    clear_props()


if __name__ == "__main__":
    register()

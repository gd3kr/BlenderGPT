import sys
import os
import bpy

# Add the 'libs' folder to the Python path
libs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
if libs_path not in sys.path:
    sys.path.append(libs_path)

print (libs_path)
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

bl_info = {
    "name": "GPT-4 Blender Assistant",
    "blender": (2, 82, 0),
    "category": "Object",
    "author": "Aarya (@gd3kr)",
    "version": (1, 0, 0),
    "location": "3D View > UI > GPT-4 Blender Assistant",
    "description": "Generate Blender Python code using OpenAI's GPT-4 to perform various tasks.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
}


def init_props():
    bpy.types.Scene.gpt4_natural_language_input = bpy.props.StringProperty(
        name="Command",
        description="Enter the natural language command",
        default="",
    )
    bpy.types.Scene.gpt4_button_pressed = bpy.props.BoolProperty(default=False)



def clear_props():
    del bpy.types.Scene.gpt4_natural_language_input
    del bpy.types.Scene.gpt4_button_pressed


def generate_blender_code(prompt):

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a assistant made for the purposes of helping the user with Blender, the 3D software. Reply only with the code, without markdown, preferably import entire modules instead of bits. do not perform destructive operations on the meshes. Do not use cap_ends. Do not do more than what is asked (setting up render settings, adding cameras, etc)"
            },
                {"role": "user", "content": "Hey, can you please create Blender code for me that accomplishes the following task: " + prompt + "? \n" + "code:\n"}
            ],
            stream=True,
            max_tokens=1000,
        )
    except Exception as e: # Use GPT-3.5 if GPT-4 is not available
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a assistant made for the purposes of helping the user with Blender, the 3D software. Reply only with the code, without markdown, preferably import entire modules instead of bits. do not perform destructive operations on the meshes. Do not use cap_ends. Do not do more than what is asked (setting up render settings, adding cameras, etc)"
            },
                {"role": "user", "content": "Hey, can you please create Blender code for me that accomplishes the following task: " + prompt + "? \n" + "code:\n"}
            ],
            stream=True,
            max_tokens=1000,
        )
        return None

    try:
        collected_events = []
        completion_text = ''
        # iterate through the stream of events
        for event in response:
            # check if role key is present in event['choices'][0]['delta']
            if 'role' in event['choices'][0]['delta']:
                # skip
                continue
            # check if length of event['choices'][0]['delta']['content'] is 0
            if len(event['choices'][0]['delta']) == 0:
                # skip
                continue
            collected_events.append(event)  # save the event response
            # extract the text
            event_text = event['choices'][0]['delta']['content']
            completion_text += event_text  # append the text
            # clear print screen
            print(completion_text, flush=True, end='\r')
            # print the text
        return completion_text
    except IndexError:
        return None


class GPT4_PT_Panel(bpy.types.Panel):
    bl_label = "GPT-4 Blender Assistant"
    bl_idname = "GPT4_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GPT-4 Assistant'

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)

        column.label(text="Enter a natural language command:")

        # Add the input field for natural language commands
        column.prop(context.scene, "gpt4_natural_language_input", text="")

        # Execute the operator with the input from the user
        button_label = "Please wait...(this might take some time)" if context.scene.gpt4_button_pressed else "Execute"
        operator = column.operator("gpt4.execute", text=button_label)
        operator.natural_language_input = context.scene.gpt4_natural_language_input

        column.separator()


class GPT4_OT_Execute(bpy.types.Operator):
    bl_idname = "gpt4.execute"
    bl_label = "GPT-4 Execute"
    bl_options = {'REGISTER', 'UNDO'}

    natural_language_input: bpy.props.StringProperty(
        name="Command",
        description="Enter the natural language command",
        default="",
    )

    def execute(self, context):
        context.scene.gpt4_button_pressed = True
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        
        blender_code = generate_blender_code(self.natural_language_input)

        if blender_code:
            # Add this line to print the generated code.
            print("Generated code:", blender_code)
            try:
                exec(blender_code)
            except Exception as e:
                self.report({'ERROR'}, f"Error executing generated code: {e}")
                context.scene.gpt4_button_pressed = False
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "Failed to generate Blender Python code")
            context.scene.gpt4_button_pressed = False
            return {'CANCELLED'}

        context.scene.gpt4_button_pressed = False
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(GPT4_OT_Execute.bl_idname)


def register():
    bpy.utils.register_class(GPT4_OT_Execute)
    bpy.utils.register_class(GPT4_PT_Panel)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)
    init_props()


def unregister():
    bpy.utils.unregister_class(GPT4_OT_Execute)
    bpy.utils.unregister_class(GPT4_PT_Panel)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    clear_props()


if __name__ == "__main__":
    register()

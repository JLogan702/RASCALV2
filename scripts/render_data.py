import os
from jinja2 import Environment, FileSystemLoader

# Manually define working paths
cwd = os.getcwd()
template_dir = os.path.join(cwd, 'templates')
output_dir = os.path.join(cwd, 'docs')

# Show paths for debugging
print(f"🔍 Template path: {template_dir}")
print(f"📁 Output path: {output_dir}")

# Initialize Jinja2 environment
env = Environment(loader=FileSystemLoader(template_dir))

def render_template(template_file, output_file, context):
    try:
        template = env.get_template(template_file)
    except Exception as e:
        print(f"❌ Template error: {e}")
        return

    output_path = os.path.join(output_dir, output_file)
    try:
        with open(output_path, 'w') as f:
            f.write(template.render(context))
        print(f"✅ Rendered: {output_file}")
    except Exception as e:
        print(f"❌ Render error: {e}")


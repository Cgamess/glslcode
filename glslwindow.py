licence = r"""
Copyright 2024 Calvin Larsen:
                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU Affero General Public License is a free, copyleft license for
software and other kinds of works, specifically designed to ensure
cooperation with the community in the case of network server software.

The Rest is in ./LICENCE
https://github.com/Cgamess/glslcode
""" 
if 0: print(licence) # assigned it to a var and put it in a print statement to keep it in the code after compilation
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = r"glslcode: https://github.com/Cgamess/glslcode"+"\n"+licence
import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import numpy as np
import time
import json
tkroot = tk.Tk()
tkroot.withdraw()  # Hide the main window
def open_file_dialog(types=[("PNG files", "*.png")], title="Image"):
    
    file_path = filedialog.askopenfilename(filetypes=types, title=title)
    
    return file_path

# Vertex shader source code
VERTEX_SHADER = open(open_file_dialog([("glsl files", "*.glsl")],"vertex")).read()

# Fragment shader source code
FRAGMENT_SHADER = open(open_file_dialog([("glsl files", "*.glsl")],"frag")).read()

# Fragment shader Json config
FRAGMENT_SHADER_CONFIG = json.loads(open(open_file_dialog([("json files", "*.json")],"frag config")).read())


def initialize_pygame():
    pygame.init()
    display = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)

def load_texture(filename):
    # Load image using PIL (Pillow)
    image = Image.open(filename)
    image_data = image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

    # Get image dimensions
    width, height = image.size

    # Generate OpenGL texture
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    # Set texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Unbind texture
    glBindTexture(GL_TEXTURE_2D, 0)

    return texture_id

def main():
    # Initialize Pygame and OpenGL context
    initialize_pygame()

    # Open file dialog to select PNG image
    filename = open_file_dialog()

    if filename:
        # Load texture
        texture_id = load_texture(filename)

        # Compile shaders
        shader_program = compileProgram(
            compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
            compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        )

        # Vertex data for a simple quad
        vertices = np.array([
            # positions      # texture coords
            -0.5, -0.5, 0.0,  0.0, 0.0,
             0.5, -0.5, 0.0,  1.0, 0.0,
             0.5,  0.5, 0.0,  1.0, 1.0,
            -0.5,  0.5, 0.0,  0.0, 1.0
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2,
            2, 3, 0
        ], dtype=np.uint32)

        # Vertex Array Object (VAO)
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        # Vertex Buffer Object (VBO)
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Element Buffer Object (EBO)
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        # Set vertex attribute pointers
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
        glEnableVertexAttribArray(1)

        # Unbind VAO, VBO, and EBO
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # Variables for managing frame rate
        target_fps = 120
        frame_delay = 1000000000.0 / target_fps
        last_time = time.perf_counter_ns()
        u_time = 0.0  # Initialize u_time
        sides=1
        sides=float(sides)
        u_mtime=0
        u_speed=2
        # Main loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # Calculate elapsed time
            current_time = time.perf_counter_ns()
            elapsed_time = current_time - last_time
            last_time = current_time

            # Update u_time
            u_time += elapsed_time
            
            if u_time % 40000000000:
                u_mtime-=elapsed_time
            else:
                u_mtime+=elapsed_time
            u_mtime = u_mtime%20000000000

            # Clear the screen
            glClear(GL_COLOR_BUFFER_BIT)

            # Use shader program
            glUseProgram(shader_program)


            # Set u_time uniform in the shader
            glUniform1f(glGetUniformLocation(shader_program, "u_time"), float(u_time))
            glUniform1f(glGetUniformLocation(shader_program, "u_mtime"), float(u_mtime))
            
            for i in FRAGMENT_SHADER_CONFIG["SETTINGS"]:
                glUniform1f(glGetUniformLocation(shader_program, i), FRAGMENT_SHADER_CONFIG["SETTINGS"][i])

            # Bind texture
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glUniform1i(glGetUniformLocation(shader_program, "textureSampler"), 0)

            # Draw quad
            glBindVertexArray(vao)
            glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
            glBindVertexArray(0)

            # Update the display
            pygame.display.flip()

    else:
        print("No file selected")

    # Cleanup
    glDeleteTextures(1, np.array([texture_id], dtype=np.uint32))
    glDeleteProgram(shader_program)
    glDeleteBuffers(1, np.array([vbo], dtype=np.uint32))
    glDeleteBuffers(1, np.array([ebo], dtype=np.uint32))
    glDeleteVertexArrays(1, np.array([vao], dtype=np.uint32))

    # Quit Pygame
    pygame.quit()

if __name__ == "__main__":
    main()

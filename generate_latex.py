# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 14:38:09 2024

@author: frede
"""

from pylatex import Document, Figure, SubFigure, NoEscape
import os

def generate_latex_with_images(folder_path):
    # Initialize the document
    doc = Document()
    
    # Add necessary packages to handle images
    doc.packages.append(NoEscape(r'\usepackage{graphicx}'))  # For including images
    doc.packages.append(NoEscape(r'\usepackage{subcaption}'))  # For subfigures
    
    # List all PNG files in the folder
    png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
    
    # Sort files to ensure consistent order
    png_files.sort()
    
    # Iterate over files in pairs
    for i in range(0, len(png_files), 2):
        with doc.create(Figure(position='h!')) as fig:
            # Add first image of the pair
            with fig.create(SubFigure(
                    position='b',
                    width=NoEscape(r'0.5\linewidth'))) as subfig:
                subfig.add_image(os.path.join(folder_path, png_files[i]),
                                 width=NoEscape(r'\linewidth'))
                subfig.add_caption(png_files[i])
            
            # Add second image if it exists
            if i + 1 < len(png_files):
                with fig.create(SubFigure(
                        position='b',
                        width=NoEscape(r'0.5\linewidth'))) as subfig:
                    subfig.add_image(os.path.join(folder_path, png_files[i+1]),
                                     width=NoEscape(r'\linewidth'))
                    subfig.add_caption(png_files[i+1])
            
            fig.add_caption(f"Images {i+1} and {i+2}")

    # Generate the LaTeX document as a string
    latex_str = doc.dumps()
    return latex_str

# For demonstration purposes, this function call will be commented out because we cannot execute it in this environment
# However, in a live Python environment with PyLaTeX installed and accessible PNG files, this would generate the LaTeX document.
# folder_path = "path/to/your/folder"
# print(generate_latex_with_images(folder_path))

path = './results/AC_compare_Vertical_interval_afternoon'
latex = generate_latex_with_images(path)








# This is the version that works:
from pylatex import Document, Figure, SubFigure, NoEscape
import os

def generate_latex_with_adjustbox_images(folder_path):
    # Initialize the document
    doc = Document()
    
    # Add necessary packages to handle images and adjustments
    doc.packages.append(NoEscape(r'\usepackage{graphicx}'))  # For including images
    doc.packages.append(NoEscape(r'\usepackage{subcaption}'))  # For subfigures
    doc.packages.append(NoEscape(r'\usepackage{adjustbox}'))  # For adjustbox features
    
    # List all PNG files in the folder
    png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
    
    # Sort files to ensure consistent order
    png_files.sort()
    
    # Iterate over files in pairs
    for i in range(0, len(png_files), 2):
        #with doc.create(Figure(position='h!')) as fig:
        with doc.create(Figure(position='H')) as fig:
            # Embed the adjustbox environment with max width and centering
            fig.append(NoEscape(r'\begin{adjustbox}{max width=1.2\linewidth,center}'))
            
            # Add first image of the pair
            with fig.create(SubFigure(
                    position='b',
                    width=NoEscape(r'.55\textwidth'))) as subfig:
                subfig.add_image(os.path.join(folder_path, png_files[i]),
                                 width=NoEscape(r'\linewidth'))
                subfig.add_caption(png_files[i])
            
            # Add second image if it exists
            if i + 1 < len(png_files):
                with fig.create(SubFigure(
                        position='b',
                        width=NoEscape(r'.55\textwidth'))) as subfig:
                    subfig.add_image(os.path.join(folder_path, png_files[i+1]),
                                     width=NoEscape(r'\linewidth'))
                    subfig.add_caption(png_files[i+1])

            # Close the adjustbox environment
            fig.append(NoEscape(r'\end{adjustbox}'))
            
            # Add overall caption and label for the figure
            fig.add_caption(f"Images {i+1} and {i+2}")
            fig.append(NoEscape(r'\label{fig:test}'))

    # Generate the LaTeX document as a string
    latex_str = doc.dumps()
    return latex_str

# Example usage:
# folder_path = "path/to/your/images"
# print(generate_latex_with_adjustbox_images(folder_path))

lax2 = generate_latex_with_adjustbox_images(path)





# Best version so far
from pylatex import Document, Figure, SubFigure, NoEscape
import os

def generate_latex_with_adjustbox_images(folder_path):
    # Initialize the document
    doc = Document()
    
    # Add necessary packages to handle images and adjustments
    doc.packages.append(NoEscape(r'\usepackage{graphicx}'))  # For including images
    doc.packages.append(NoEscape(r'\usepackage{subcaption}'))  # For subfigures
    doc.packages.append(NoEscape(r'\usepackage{adjustbox}'))  # For adjustbox features
    
    # List all PNG files in the folder
    png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
    
    # Sort files to ensure consistent order
    png_files.sort()
    
    # Iterate over files in pairs
    for i in range(0, len(png_files), 2):
        # Create figure environment with specific positioning
        with doc.create(Figure(position='H')) as fig:
            # Embed the adjustbox environment with max width and centering
            fig.append(NoEscape(r'\begin{adjustbox}{max width=1.2\linewidth,center}'))
            
            # Add first image of the pair
            with fig.create(SubFigure(
                    position='b',
                    width=NoEscape(r'.55\textwidth'))) as subfig:
                subfig.add_image(os.path.join(folder_path, png_files[i]),
                                 width=NoEscape(r'\linewidth'))
                subfig.add_caption(png_files[i])
            
            # Add second image if it exists
            if i + 1 < len(png_files):
                with fig.create(SubFigure(
                        position='b',
                        width=NoEscape(r'.55\textwidth'))) as subfig:
                    subfig.add_image(os.path.join(folder_path, png_files[i+1]),
                                     width=NoEscape(r'\linewidth'))
                    subfig.add_caption(png_files[i+1])

            # Close the adjustbox environment
            fig.append(NoEscape(r'\end{adjustbox}'))
            
            # Add overall caption for the figure
            fig.add_caption(f"Images {i+1} and {i+2}")
            
            # Dynamically generate figure label based on the file name of the first image
            # You can modify this to include both names or format it as you need
            label_name = "fig:" + os.path.splitext(png_files[i])[0]  # Removes extension and adds prefix
            fig.append(NoEscape(fr'\label{{{label_name}}}'))

    # Generate the LaTeX document as a string
    latex_str = doc.dumps()
    return latex_str

lax3 = generate_latex_with_adjustbox_images(path)





from pylatex import Document, Figure, SubFigure, NoEscape
import os

def generate_latex_with_adjustbox_images(folder_path):
    # Initialize the document
    doc = Document()
    
    # Add necessary packages to handle images and adjustments
    doc.packages.append(NoEscape(r'\usepackage{graphicx}'))  # For including images
    doc.packages.append(NoEscape(r'\usepackage{subcaption}'))  # For subfigures
    doc.packages.append(NoEscape(r'\usepackage{adjustbox}'))  # For adjustbox features
    
    # List all PNG files in the folder
    png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
    
    # Sort files to ensure consistent order
    png_files.sort()
    
    # Iterate over files in pairs
    for i in range(0, len(png_files), 2):
        # Create figure environment with specific positioning
        with doc.create(Figure(position='H')) as fig:
            # Embed the adjustbox environment with max width and centering
            fig.append(NoEscape(r'\begin{adjustbox}{max width=1.2\linewidth,center}'))
            
            # Add first image of the pair
            with fig.create(SubFigure(
                    position='b',
                    width=NoEscape(r'.55\textwidth'))) as subfig:
                image_path = os.path.join(folder_path, png_files[i])
                subfig.add_image(image_path, width=NoEscape(r'\linewidth'))
                
                # Custom caption based on file name
                if "Ref" in png_files[i] and "compare" in png_files[i]:
                    caption = "Comparison between reference cell POA irradiance and modelled POA irradiance. The modelled POA is “fuel in” irradiance to be comparable with a reference cell."
                else:
                    caption = png_files[i]
                subfig.add_caption(caption)
            
            # Add second image if it exists
            if i + 1 < len(png_files):
                with fig.create(SubFigure(
                        position='b',
                        width=NoEscape(r'.55\textwidth'))) as subfig:
                    image_path = os.path.join(folder_path, png_files[i+1])
                    subfig.add_image(image_path, width=NoEscape(r'\linewidth'))
                    
                    # Custom caption based on file name
                    if "ref" in png_files[i+1] and "compare" in png_files[i+1]:
                        caption = "Comparison between reference cell POA irradiance and modelled POA irradiance. The modelled POA is “fuel in” irradiance to be comparable with a reference cell."
                    else:
                        caption = png_files[i+1]
                    subfig.add_caption(caption)

            # Close the adjustbox environment
            fig.append(NoEscape(r'\end{adjustbox}'))
            
            # Add overall caption for the figure
            fig.add_caption(f"Images {i+1} and {i+2}")
            
            # Dynamically generate figure label based on the file name of the first image
            label_name = "fig:" + os.path.splitext(png_files[i])[0]  # Removes extension and adds prefix
            fig.append(NoEscape(fr'\label{{{label_name}}}'))

    # Generate the LaTeX document as a string
    latex_str = doc.dumps()
    return latex_str

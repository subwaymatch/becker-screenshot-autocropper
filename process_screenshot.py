from PIL import Image, ImageDraw
import math
import glob
import numpy as np
import re
import easyocr
import hashlib
import pathlib
from datetime import datetime

def get_file_checksum(image_file):
    file_checksum = hashlib.md5(image_file.read()).hexdigest()
    return file_checksum

def autocrop_screenshot(image_file):
    im = Image.open(image_file)
    img_width, img_height = im.size

    px = im.load()

    LEFT_RED_LINE_RGB = (204, 72, 20)
    WHITE_RGB = (255, 255, 255)

    red_line_start_x = None
    red_line_end_x = None

    # find the starting and ending x positions of the red vertical line
    for x in range(img_width):
        y = img_height - 1
        pixel_RGB = px[x, y]

        if pixel_RGB == LEFT_RED_LINE_RGB:
            red_line_end_x = x

            if not red_line_start_x:
                red_line_start_x = x

        elif red_line_end_x:
            break

    print(f'red_line_start_x={red_line_start_x}, red_line_end_x={red_line_end_x}')




    # the question whitebox starts after the red vertical
    whitebox_start_x = whitebox_start_x = red_line_end_x + 1
    whitebox_end_x = None
    whitebox_start_y = None
    whitebox_end_y = img_height - 1

    # find white box's ending x position
    for x in range(red_line_end_x + 1, img_width):
        y = whitebox_end_y
        pixel_RGB = px[x, y]

        if pixel_RGB == WHITE_RGB:
            whitebox_end_x = x
        else:
            break

    # find whitebox's starting y position
    for y in reversed(range(0, whitebox_end_y + 1)):
        x = whitebox_start_x
        pixel_RGB = px[x, y]

        if pixel_RGB == WHITE_RGB:
            whitebox_start_y = y
        else:
            break

    print(f'whitebox_start_x={whitebox_start_x}, whitebox_end_x={whitebox_end_x}')
    print(f'whitebox_start_y={whitebox_start_y}, whitebox_end_y={whitebox_end_y}')



    header_start_y = None
    header_end_y = None

    # find the starting y position of the question header
    for y in range(whitebox_start_y, whitebox_end_y):
        for x in range(whitebox_start_x, whitebox_end_x):
            pixel_RGB = px[x, y]

            if pixel_RGB != WHITE_RGB:
                header_start_y = y
                break

        if header_start_y:
            break

    # find the ending y position of the question header
    for y in range(header_start_y + 1, whitebox_end_y):
        is_line_blank = True
        
        for x in range(whitebox_start_x, whitebox_end_x):
            pixel_RGB = px[x, y]

            if pixel_RGB != WHITE_RGB:
                is_line_blank = False
                break

        if is_line_blank:
            header_end_y = y
            break

    print(f'header_start_y={header_start_y}, header_end_y={header_end_y}')




    BLUE_HEADER_RGB = (4, 58, 78)
    blue_header_end_y = None

    # find the starting and ending x positions of the red vertical line
    for y in range(header_start_y):
        pixel_RGB = px[0, y]
        
        if pixel_RGB == BLUE_HEADER_RGB:
            blue_header_end_y = y
        else:
            break
            
    print(f'blue_header_end_y={blue_header_end_y}')

    im_exam_header = im.crop((
        0,
        0,
        img_width - 1,
        blue_header_end_y)
    )

    ocr_reader = easyocr.Reader(['en'])
    ocr_result = ocr_reader.readtext(np.array(im_exam_header))
    exam_section = None

    for r in ocr_result:
        matched_text = r[1].upper()

        match = re.match(r'FAR|AUD|REG|ISC|TCP|BAR', r[1].upper())

        if match:
            exam_section = match.group(0)
            break

    print(f'exam_section={exam_section}')




    bottom_arrow_start_y = None
    content_end_y = None

    # find the starting y position of the question navigation arrows at the bottom
    for y in reversed(range(whitebox_start_y, whitebox_end_y)):
        is_line_blank = True
        
        for x in range(whitebox_start_x, whitebox_end_x):
            pixel_RGB = px[x, y]

            if pixel_RGB != WHITE_RGB:
                is_line_blank = False
                break

        if not is_line_blank:
            bottom_arrow_start_y = y
        elif is_line_blank and bottom_arrow_start_y:
            break

    # find the ending y position of the question content
    for y in reversed(range(whitebox_start_y, bottom_arrow_start_y)):
        is_line_blank = True
        
        for x in range(whitebox_start_x, whitebox_end_x):
            pixel_RGB = px[x, y]

            if pixel_RGB != WHITE_RGB:
                is_line_blank = False
                break

        if not is_line_blank:
            content_end_y = y
            break

    print(f'bottom_arrow_start_y={bottom_arrow_start_y}')
    print(f'content_end_y={content_end_y}')



    # look for highlight markings
    # if an MCQ option is highlighted in green, the answer a user submitted is correct
    # if an MCQ option is highlighted in yellow, the answer a user submitted is incorrect
    HIGHLIGHT_RGB_CORRECT = (189, 223, 198)
    HIGHLIGHT_RGB_INCORRECT = (255, 255, 0)
    
    is_answered = False
    is_correct = False

    for y in range(whitebox_start_y, whitebox_end_y + 1):
        for x in range(whitebox_start_x, whitebox_end_x + 1):
            pixel_RGB = px[x, y]

            if pixel_RGB == HIGHLIGHT_RGB_CORRECT:
                is_answered = True
                is_correct = True
                break
            elif pixel_RGB == HIGHLIGHT_RGB_INCORRECT:
                is_answered = True
                is_correct = False
                break

        if is_answered:
            break

    print(f'is_answered={is_answered}, is_correct={is_correct}')



    im_question = im.crop((whitebox_start_x, whitebox_start_y, whitebox_end_x, min(img_height - 1, content_end_y + 30)))
    im_question_header = im.crop((
        whitebox_start_x,
        header_start_y,
        whitebox_end_x,
        header_end_y)
    )



    ocr_result = ocr_reader.readtext(np.array(im_question_header))
    ocr_result



    question_id = None

    for r in ocr_result:
        matched_text = r[1].upper()

        match = re.match(r'MCQ-\d+', r[1].upper())

        if match:
            question_id = match.group(0)
            break



    p = pathlib.Path(image_file.filename)

    new_filename = datetime.today().strftime('%Y%m%d')
    new_filename += f'-{exam_section}-{question_id}'

    if is_answered:
        new_filename += f'-{"correct" if is_correct else "incorrect"}'
    else:
        new_filename += '-unattempted'

    new_filename += p.suffix

    return {
        "original_filename": image_file.filename,
        "exam_section": exam_section,
        "question_id": question_id,
        "original_image_width": img_width,
        "original_img_height": img_height,
        "is_answered": is_answered,
        "is_correct": is_correct,
        "cropped_image": im_question,
        'new_filename': new_filename
    }
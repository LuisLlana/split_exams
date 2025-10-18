'''
This programs splits a pdf exam into individual student exams.

The initial page of the exam of each student has a qr code
with its id.

Te progams splits the exams and generates a pdf file
name <student_id>.pdf

The program detects the new qr codes.

The outdir is deleted if it exists and a new one is created.

Parameters

--pdf <exam_file> (defaults to 'todo.pdf')
--outdir <output_dir> (defaults to the name of the pdf file without the extension and prefixing with 'pend_', outdir defaults to 'pend_todo' if the pdf file is 'todo.pdf')
'''


import argparse
import shutil
from pathlib import Path
from pdf2image import convert_from_path, convert_from_bytes
import numpy as np
import cv2

def save_images(images: list, outdir:Path, ant:str):
    outfile = outdir / f'{ant}.pdf'
    print(f'Saving {len(images)} images to {outfile}')
    images[0].save(outfile, save_all=True, append_images=images[1:], quality=95)
    print('Done saving.')

def generate_individual_exams(pdf_file: Path, outdir: Path) -> None:
    print(f'Reading {pdf_file}...', flush=True)
    images = convert_from_path(pdf_file, fmt='jpg')
    print('done.')
    ant_id = ''
    qcd = cv2.QRCodeDetector()
    image_current = []
    for _, image in enumerate(images):
        retval, decoded_info, points, straight_qrcode = qcd.\
            detectAndDecodeMulti(np.asarray(image))
        if retval:
            student_id = decoded_info[0]
            if student_id != ant_id:
                if ant_id != '':
                    print(f'\nSaving {ant_id}...')
                    save_images(image_current, outdir, ant_id)
                print(f'Found new student student {student_id}...', flush=True)
                ant_id = student_id
                image_current = [image]
            else:
                image_current.append(image)
        else:
            image_current.append(image)
    if ant_id != '':
        save_images(image_current, outdir, ant_id)

def main():
    argparser = argparse.ArgumentParser(description='Split exams into individual student exams.')
    argparser.add_argument('--pdf', type=str, default='todo.pdf',
                            help='PDF file to split into individual student exams.')
    argparser.add_argument('--outdir', type=str, default='',
                           help='Output directory for individual student exams.')
    args = argparser.parse_args()
    if args.outdir == '':
        outdir = Path(f'pend_{Path(args.pdf).stem}')
    else:
        outdir = Path(args.outdir)
    pdf_file = Path(args.pdf)
    shutil.rmtree(outdir, ignore_errors=True)
    outdir.mkdir()
    generate_individual_exams(pdf_file, outdir)


if __name__ == '__main__':
    main()

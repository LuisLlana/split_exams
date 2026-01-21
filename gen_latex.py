'''
Generates LaTeX commands for exams for students in a csv.
The exam LaTeX file has the following commands
\\newcommand{\\nombre}{\\enspace}
\\newcommand{\\email}{\\enspace}
\\newcommand{\\grupo}{\\enspace}
\\newcommand{\\qr}{\\hbox to 1cm{\\vbox to 1cm{\\vss}\\hss}}

These command will be replaced by the student's name,
email, group, and QR code respectively.

The program will generate an exam for each student with the same name
as the original one with a prefix student_id.
The student id is the email of the student without the @XXXX part.

All the exams will be generated in a directory with the same name as
the group.

The program will delete the group directory if it exists and create a new one.
with all the axuiliary files as in the folder exam

        usage: gen_latex.py [-h] [--destdir DESTDIR] -f CSVFILE exam

        Generate Exams to students

        positional arguments:
          exam                  Exam template file

        options:
          -h, --help             show this help message and exit
          --destdir DESTDIR      Destir of PDF files, defaults to exam without the suffix
          -f, --csvfile CSVFILE  CSV file with the student data, default: alumnos.csv

The student file is a CSV file with the following columns, downloaded from
GEA

FOTOGRAFÍA,NOMBRE COMPLETO,DOCUMENTO,MAT.,CONV.,OBSERVACIÓN,CORREO,MOODLE_ID ,"Abellán Lapeña, Daniel",49147886Z,1,1,,daniab01@ucm.es,6640
,"AIT EL HAJ SABIH, HAFSA",03477456V,1,1,,hafsaait@ucm.es,6641

'''


from csv import DictReader
import sys
import argparse
from pathlib import Path
import shutil
import re
from  multiprocessing import Pool
import shlex, subprocess
import os
from typing import Callable, TypedDict
from dataclasses import dataclass


from pylatexenc.latexencode import unicode_to_latex

class StatusDict(TypedDict):
    student: str
    status: str

class StudentDict(TypedDict):
    firstname: str
    lastname: str
    email: str

class Exam:
    def __init__(self, exam: Path, destdir: Path) -> None:
        self._exam = exam
        self._destdir = destdir
        self._examtext = self._exam.read_text()
        self._generate_group_dir()

    @property
    def exam(self) -> Path:
        return self._exam

    @property
    def destdir(self) -> Path:
        return self._destdir

    @property
    def examtext(self) -> str:
        return self._examtext


    def _generate_group_dir(self) -> None:
        if self.destdir.exists():
            shutil.rmtree(self.destdir)
        self.destdir.mkdir()
        # examdir = self.exam.parent
        # shutil.copytree(examdir, self.group)


    def _generate_exam(self, student_id: str, student_name: str) -> str:
        student_name = unicode_to_latex(student_name)
        student_name = student_name.replace('\\', '\\\\')
        examtext = self.examtext
        examtext = re.sub(r'\\newcommand\{\\nombre\}.*',
                               f'\\\\newcommand{{\\\\nombre}}{{{student_name}}}',
                          examtext)
        examtext = re.sub(r'\\newcommand\{\\email\}.*',
                          f'\\\\newcommand{{\\\\email}}{{{student_id}}}',
                          examtext)
        examtext = re.sub(r'\\newcommand\{\\grupo\}.*',
                          f'\\\\newcommand{{\\\\grupo}}{{{self.destdir.name}}}',
                          examtext)
        return examtext


    def generate_pdf(self, ordered_student: tuple[int, StudentDict])\
            -> StatusDict:
        student = ordered_student[1]
        order = ordered_student[0]
        student_id = student['email'].split('@')[0]
        student_name = f'{student['lastname']}, {student['firstname']}'
        st_exam = self._generate_exam(student_id, student_name)
        st_exam_path = Path(f'{order:03}_{student_id}_{self.exam.name}')
        st_exam_path.write_text(st_exam)
        print(f'Generating exam for student: {student_name} ({student_id}) in {st_exam_path.name}...')
        for _ in range(3):
            cmd = shlex.split(f'pdflatex  -interaction=nonstopmode -halt-on-error {st_exam_path}')
            rcode = subprocess.run(cmd, # cwd=self.group,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                                   )
            if rcode.returncode != 0:
                print(f'Error generating PDF: {rcode.returncode} {student_id}')
                return {'student': student_id,
                        'status': 'ERROR'}
            # move the pdf to the group directory
        pdf_name = st_exam_path.with_suffix('.pdf').name
        shutil.move(pdf_name, self.destdir)
        # clean auxiliary files
        for ext in ['.aux', '.log', '.tex']:
            aux_file = st_exam_path.with_suffix(ext)
            if aux_file.exists():
                aux_file.unlink()
                #shutil.move(aux_file, self.group)
        print(f'Exam for student {student_name} ({student_id}) generated successfully.')
        return {'student': student_id,
                'status': 'OK'}



def row2student(row: dict[str, str]) -> StudentDict:
    '''Convert a CSV row to a StudentDict
FOTOGRAFÍA,NOMBRE COMPLETO,DOCUMENTO,MAT.,CONV.,OBSERVACIÓN,CORREO,MOODLE_ID ,"Abellán Lapeña, Daniel",49147886Z,1,1,,daniab01@ucm.es,6640
,"AIT EL HAJ SABIH, HAFSA",03477456V,1,1,,hafsaait@ucm.es,6641
    '''
    lastname, firstname = row['NOMBRE COMPLETO'].split(',')
    return {'firstname': firstname.strip(),
            'lastname': lastname.strip(),
            'email': row['CORREO']}

def generate_exams(exam: Exam,
                   student_file: Path) -> list[StatusDict]:
    print(f'Reading students from {student_file}...')
    with open(student_file, 'r') as fl:
        students = enumerate(sorted(map(row2student, DictReader(fl)),
                                    key=lambda s: (s['lastname'], s['firstname'])))
        pool = Pool()
        lst = list(pool.map(exam.generate_pdf, list(students)))
    return lst

def main() -> None:
    parser = argparse.ArgumentParser(description='Generate Exams to students')
    parser.add_argument('--destdir', type=Path,
                        default=None, help='Destir of PDF files, defaults to exam without the suffix')
    parser.add_argument('-f', '--csvfile', type=Path, required=True,
                        default=Path('alumnos.csv'),
                        help='CSV file with the student data, default: alumnos.csv')
    parser.add_argument('exam', type=Path,
                        help='Exam template file')

    args = parser.parse_args()
    destdir = args.destdir

    if destdir is None:
        destdir = args.exam.with_suffix('')

    exam = Exam(args.exam, destdir)
    csvfile = args.csvfile

    print(f'Generating exams in directory {destdir} from {csvfile}...')
    status = generate_exams(exam, csvfile)
    error_lst = list(filter(lambda s: s['status'] == 'ERROR',
                            status))
    error_count = len(error_lst)
    if error_count > 0:
        print(f'Error generating {error_count} exams.')
        for s in error_lst:
            print(f"{s['student']}")
    else:
        print('All exams generated successfully.')


if __name__ == '__main__':
            main()

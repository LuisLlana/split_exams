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

Parameters
--exam <exam_file> (defaults to 'exam.tex'
--group <group_name> (defaults to 'group')
--student_file <student_file> (defaults to 'group.csv')
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
    name: str
    email: str

class Exam:
    def __init__(self, exam: Path, group: Path) -> None:
        self._exam = exam
        self._group = group
        self._examtext = self._exam.read_text()
        self._generate_group_dir()

    @property
    def exam(self) -> Path:
        return self._exam

    @property
    def group(self) -> Path:
        return self._group

    @property
    def examtext(self) -> str:
        return self._examtext


    def _generate_group_dir(self) -> None:
        if self.group.exists():
            shutil.rmtree(self.group)
        examdir = self.exam.parent
        shutil.copytree(examdir, self.group)


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
                          f'\\\\newcommand{{\\\\grupo}}{{{self.group.name}}}',
                          examtext)
        return examtext


    def generate_pdf(self, student: StudentDict) -> StatusDict:
        student_id = student['email'].split('@')[0]
        student_name = student['name']
        st_exam = self._generate_exam(student_id, student_name)
        st_exam_path = Path(f'{student_id}_{self.exam.name}')
        (self.group / st_exam_path).write_text(st_exam)
        print(f'Generating exam for student: {student_name} ({student_id}) in {st_exam_path.name}...')
        for _ in range(3):
            cmd = shlex.split(f'pdflatex  -interaction=nonstopmode -halt-on-error {st_exam_path}')
            rcode = subprocess.run(cmd, cwd=self.group,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
            if rcode.returncode != 0:
                print('Error generating PDF')
                return {'student': student_id,
                        'status': 'ERROR'}
            print(f'Exam for student {student_name} ({student_id}) generated successfully.')
        return {'student': student_id,
                'status': 'OK'}


def generate_exams(exam: Exam,
                   student_file: Path) -> list[StatusDict]:
    with open(student_file, 'r') as fl:
        students = list(DictReader(fl))
        print(f"c1, {students}")
        pool = Pool()
        lst = list(pool.map(exam.generate_pdf, students))
    return lst

def main() -> None:
    parser = argparse.ArgumentParser(description='Generate Exams to students')
    parser.add_argument('--exam', type=str,
                        default='exam.tex', help='Exam template file')
    parser.add_argument('--group', type=str,
                        default='group', help='Group name for the exams')
    parser.add_argument('--student_file', type=str,
                        help = 'CSV file with students data, defaults to the argument of group ended in .csv',
                        default='')
    args = parser.parse_args()

    exam = Exam(Path(args.exam), Path(args.group))
    student_file = args.student_file
    if args.student_file == '':
        student_file = Path(f'{args.group}.csv')
    else:
        student_file = Path(args.student_file)

    status = generate_exams(exam, student_file)
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


import json
import os


class Student:
    def __init__(self, name, student_id, grade):
        self.name = name
        self.student_id = student_id
        self.grade = grade

    def to_dict(self):
        return {
            "name": self.name,
            "student_id": self.student_id,
            "grade": self.grade
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            data["student_id"],
            data["grade"]
        )


class StudentManager:
    def __init__(self, filename="students.json"):
        self.filename = filename
        self.students = []
        self.load_students()

    def load_students(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as file:
                    data = json.load(file)

                self.students = [
                    Student.from_dict(student)
                    for student in data
                ]

            except (json.JSONDecodeError, FileNotFoundError):
                self.students = []

    def save_students(self):
        with open(self.filename, "w") as file:
            json.dump(
                [student.to_dict() for student in self.students],
                file,
                indent=4
            )

    def add_student(self, student):
        for existing_student in self.students:
            if existing_student.student_id == student.student_id:
                print("Error: Student ID already exists.")
                return

        self.students.append(student)
        self.save_students()
        print("Student added successfully.")

    def list_students(self):
        if not self.students:
            print("No students found.")
            return

        print("\n--- Student Records ---")
        print(f"{'ID':<15}{'Name':<25}{'Grade':<10}")
        print("-" * 50)

        for student in self.students:
            print(
                f"{student.student_id:<15}"
                f"{student.name:<25}"
                f"{student.grade:<10}"
            )

    def update_student(self, student_id):
        for student in self.students:
            if student.student_id == student_id:
                new_name = input("Enter new name: ").strip()
                new_grade = input("Enter new grade: ").strip()

                if new_name:
                    student.name = new_name

                if new_grade:
                    student.grade = new_grade

                self.save_students()
                print("Student updated successfully.")
                return

        print("Student not found.")

    def delete_student(self, student_id):
        for student in self.students:
            if student.student_id == student_id:
                self.students.remove(student)
                self.save_students()
                print("Student deleted successfully.")
                return

        print("Student not found.")


def main():
    manager = StudentManager()

    while True:
        print("\n===== Student Management System =====")
        print("1. Add Student")
        print("2. List Students")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            name = input("Enter student name: ").strip()
            student_id = input("Enter student ID: ").strip()
            grade = input("Enter student grade: ").strip()

            if not name or not student_id or not grade:
                print("Error: All fields are required.")
                continue

            student = Student(name, student_id, grade)
            manager.add_student(student)

        elif choice == "2":
            manager.list_students()

        elif choice == "3":
            student_id = input("Enter student ID to update: ").strip()
            manager.update_student(student_id)

        elif choice == "4":
            student_id = input("Enter student ID to delete: ").strip()
            manager.delete_student(student_id)

        elif choice == "5":
            print("Program ended.")
            break

        else:
            print("Invalid option. Please choose 1-5.")


if __name__ == "__main__":
    main()


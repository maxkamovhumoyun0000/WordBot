"""
Math Quiz Module - Trigonometry
Hidden Section: Unlocks with code "0107"
Contains trigonometric values for all standard angles with multiple choice variants
"""

import random
from typing import List, Tuple, Dict

# Trigonometric values database
MATH_TRIGONOMETRY_DATA = {
    0: {"sin": "0", "cos": "1", "tan": "0", "ctg": "aniqlanmagan"},
    30: {"sin": "1/2", "cos": "√3/2", "tan": "1/√3", "ctg": "√3"},
    45: {"sin": "√2/2", "cos": "√2/2", "tan": "1", "ctg": "1"},
    60: {"sin": "√3/2", "cos": "1/2", "tan": "√3", "ctg": "1/√3"},
    90: {"sin": "1", "cos": "0", "tan": "aniqlanmagan", "ctg": "0"},
    120: {"sin": "√3/2", "cos": "-1/2", "tan": "-√3", "ctg": "-1/√3"},
    135: {"sin": "√2/2", "cos": "-√2/2", "tan": "-1", "ctg": "-1"},
    150: {"sin": "1/2", "cos": "-√3/2", "tan": "-1/√3", "ctg": "-√3"},
    180: {"sin": "0", "cos": "-1", "tan": "0", "ctg": "aniqlanmagan"},
    210: {"sin": "-1/2", "cos": "-√3/2", "tan": "1/√3", "ctg": "√3"},
    225: {"sin": "-√2/2", "cos": "-√2/2", "tan": "1", "ctg": "1"},
    240: {"sin": "-√3/2", "cos": "-1/2", "tan": "√3", "ctg": "1/√3"},
    270: {"sin": "-1", "cos": "0", "tan": "aniqlanmagan", "ctg": "0"},
    300: {"sin": "-√3/2", "cos": "1/2", "tan": "-√3", "ctg": "-1/√3"},
    315: {"sin": "-√2/2", "cos": "√2/2", "tan": "-1", "ctg": "-1"},
    330: {"sin": "-1/2", "cos": "√3/2", "tan": "-1/√3", "ctg": "-√3"},
    360: {"sin": "0", "cos": "1", "tan": "0", "ctg": "aniqlanmagan"},
}

# Variant answers for each trigonometric function
VARIANTS = {
    "sin": {
        "correct_options": [
            "0", "1/2", "√2/2", "√3/2", "1", "-1/2", "-√2/2", "-√3/2", "-1"
        ],
        "wrong_options": [
            "1/3", "2/3", "√3/3", "-1/3", "-2/3", "√2/3", "1/4", "3/4", "2"
        ]
    },
    "cos": {
        "correct_options": [
            "0", "1/2", "√2/2", "√3/2", "1", "-1/2", "-√2/2", "-√3/2", "-1"
        ],
        "wrong_options": [
            "1/3", "2/3", "√3/3", "-1/3", "-2/3", "√2/3", "1/4", "3/4", "2"
        ]
    },
    "tan": {
        "correct_options": [
            "0", "1/√3", "1", "√3", "-1/√3", "-1", "-√3", "aniqlanmagan"
        ],
        "wrong_options": [
            "1/2", "√2", "2/√3", "√3/2", "-√2", "-2/√3", "1/2", "2"
        ]
    },
    "ctg": {
        "correct_options": [
            "0", "1/√3", "1", "√3", "-1/√3", "-1", "-√3", "aniqlanmagan"
        ],
        "wrong_options": [
            "1/2", "√2", "2/√3", "√3/2", "-√2", "-2/√3", "1/2", "2"
        ]
    }
}


class MathQuiz:
    """Main trigonometry quiz class with hidden section"""
    
    def __init__(self):
        self.is_unlocked = False
        self.questions_generated = []
        self.quiz_session = []
        self.current_question_index = 0
        self.score = 0
        self.total_questions = 0
        self.answered_questions = []
        
    def unlock_hidden_section(self, code: str) -> bool:
        """
        Unlock hidden section with secret code "0107"
        Returns True if code is correct, False otherwise
        """
        if code == "0107":
            self.is_unlocked = True
            return True
        return False
    
    def generate_question(self, angle: int, function: str) -> Dict:
        """
        Generate a multiple choice question for a specific angle and trig function
        
        Args:
            angle: Angle in degrees (0, 30, 45, 60, 90, etc.)
            function: "sin", "cos", "tan", or "ctg"
        
        Returns:
            Dictionary with question and variants
        """
        if angle not in MATH_TRIGONOMETRY_DATA:
            return None
        
        correct_answer = MATH_TRIGONOMETRY_DATA[angle][function]
        
        # Get variants
        correct_variants = VARIANTS[function]["correct_options"]
        wrong_variants = VARIANTS[function]["wrong_options"]
        
        # Create answer options
        options = [correct_answer]
        
        # Add some wrong variants
        wrong_selected = random.sample(wrong_variants, min(3, len(wrong_variants)))
        options.extend(wrong_selected)
        
        # Shuffle options
        random.shuffle(options)
        
        question = {
            "angle": angle,
            "function": function,
            "question_text": f"{function.upper()}({angle}°) = ?",
            "correct_answer": correct_answer,
            "options": options,
            "option_letters": ["A", "B", "C", "D"][:len(options)]
        }
        
        return question
    
    def generate_all_questions(self) -> List[Dict]:
        """
        Generate all possible questions from the trigonometry table
        Only available if hidden section is unlocked
        
        Returns:
            List of all question dictionaries
        """
        if not self.is_unlocked:
            return []
        
        all_questions = []
        angles = list(MATH_TRIGONOMETRY_DATA.keys())
        functions = ["sin", "cos", "tan", "ctg"]
        
        for angle in angles:
            for function in functions:
                question = self.generate_question(angle, function)
                if question:
                    all_questions.append(question)
        
        return all_questions
    
    def generate_quiz_session(self, num_questions: int = 10) -> List[Dict]:
        """
        Generate a random quiz session with specified number of questions
        Only available if hidden section is unlocked
        
        Args:
            num_questions: Number of questions in the quiz
        
        Returns:
            List of randomly selected questions
        """
        if not self.is_unlocked:
            return []
        
        all_questions = self.generate_all_questions()
        if len(all_questions) == 0:
            return []
        
        # Select random questions
        selected_questions = random.sample(
            all_questions, 
            min(num_questions, len(all_questions))
        )
        
        self.quiz_session = selected_questions
        self.current_question_index = 0
        self.score = 0
        self.total_questions = len(selected_questions)
        self.answered_questions = []
        
        return selected_questions
    
    def check_answer(self, question: Dict, selected_option_index: int) -> Tuple[bool, str]:
        """
        Check if the selected answer is correct
        
        Args:
            question: Question dictionary
            selected_option_index: Index of selected option (0, 1, 2, 3)
        
        Returns:
            Tuple of (is_correct, feedback_message)
        """
        selected_answer = question["options"][selected_option_index]
        is_correct = selected_answer == question["correct_answer"]
        
        if is_correct:
            feedback = f"✅ To'g'ri! {question['function'].upper()}({question['angle']}°) = {question['correct_answer']}"
            self.score += 1
        else:
            feedback = f"❌ Noto'g'ri! Siz: {selected_answer}\nTo'g'ri javob: {question['correct_answer']}"
        
        # Record answered question
        self.answered_questions.append({
            "question": question,
            "selected_answer": selected_answer,
            "is_correct": is_correct
        })
        
        return is_correct, feedback
    
    def get_next_question(self) -> Dict:
        """Get the next question from the current quiz session"""
        if not self.quiz_session or self.current_question_index >= len(self.quiz_session):
            return None
        
        question = self.quiz_session[self.current_question_index]
        self.current_question_index += 1
        
        return question
    
    def get_current_progress(self) -> Dict:
        """Get current quiz progress"""
        if self.total_questions == 0:
            return {
                "current": 0,
                "total": 0,
                "score": 0,
                "percentage": 0,
                "message": "Quiz boshlanmagan"
            }
        
        percentage = (self.score / self.total_questions) * 100
        
        return {
            "current": self.current_question_index,
            "total": self.total_questions,
            "score": self.score,
            "percentage": round(percentage, 1),
            "message": f"Savol {self.current_question_index}/{self.total_questions} | To'g'ri: {self.score}"
        }
    
    def get_quiz_results(self) -> Dict:
        """Get final quiz results"""
        if self.total_questions == 0:
            return {"status": "no_quiz"}
        
        percentage = (self.score / self.total_questions) * 100
        
        if percentage == 100:
            rating = "⭐⭐⭐ AJOYIB!"
        elif percentage >= 80:
            rating = "⭐⭐ YAXSHI!"
        elif percentage >= 60:
            rating = "⭐ O'RTACHA"
        else:
            rating = "📚 QAYTA O'RGANIB KO'RING"
        
        return {
            "total_questions": self.total_questions,
            "correct": self.score,
            "wrong": self.total_questions - self.score,
            "percentage": round(percentage, 1),
            "rating": rating,
            "details": self.answered_questions
        }
    
    def restart_quiz(self) -> None:
        """Restart the current quiz"""
        self.current_question_index = 0
        self.score = 0
        self.answered_questions = []
    
    def get_detailed_statistics(self) -> Dict:
        """Get detailed statistics by angle and function"""
        if not self.answered_questions:
            return {}
        
        stats = {
            "by_angle": {},
            "by_function": {},
            "by_angle_function": {}
        }
        
        for item in self.answered_questions:
            q = item["question"]
            angle = q["angle"]
            function = q["function"]
            is_correct = item["is_correct"]
            
            # By angle
            if angle not in stats["by_angle"]:
                stats["by_angle"][angle] = {"correct": 0, "total": 0}
            stats["by_angle"][angle]["total"] += 1
            if is_correct:
                stats["by_angle"][angle]["correct"] += 1
            
            # By function
            if function not in stats["by_function"]:
                stats["by_function"][function] = {"correct": 0, "total": 0}
            stats["by_function"][function]["total"] += 1
            if is_correct:
                stats["by_function"][function]["correct"] += 1
            
            # By angle-function pair
            key = f"{angle}°-{function}"
            if key not in stats["by_angle_function"]:
                stats["by_angle_function"][key] = {"correct": 0, "total": 0}
            stats["by_angle_function"][key]["total"] += 1
            if is_correct:
                stats["by_angle_function"][key]["correct"] += 1
        
        return stats
    
    def is_quiz_finished(self) -> bool:
        """Check if quiz is finished"""
        return self.current_question_index >= self.total_questions
    
    def get_trigonometry_table(self) -> str:
        """
        Get formatted trigonometry table as text
        Only available if hidden section is unlocked
        """
        if not self.is_unlocked:
            return "❌ Bu bo'lim maxfiy! Kod kiriting."
        
        table = "📐 **TRIGONOMETRIK GRADUSLARI JADVALI** 📐\n"
        table += "=" * 80 + "\n"
        table += f"{'Gradus':<10} {'sin x':<15} {'cos x':<15} {'tan x':<15} {'ctg x':<15}\n"
        table += "=" * 80 + "\n"
        
        for angle in sorted(MATH_TRIGONOMETRY_DATA.keys()):
            data = MATH_TRIGONOMETRY_DATA[angle]
            table += f"{angle}°{'':<7} {data['sin']:<15} {data['cos']:<15} {data['tan']:<15} {data['ctg']:<15}\n"
        
        return table
    
    def get_status(self) -> Dict:
        """Get current quiz status"""
        return {
            "is_unlocked": self.is_unlocked,
            "total_angles": len(MATH_TRIGONOMETRY_DATA),
            "total_functions": 4,
            "total_possible_questions": len(MATH_TRIGONOMETRY_DATA) * 4,
            "section_name": "MAXFIY BO'LIM - TRIGONOMETRIYA" if self.is_unlocked else "🔒 MAXFIY BO'LIM"
        }


# Example usage functions
def example_usage():
    """Example of how to use the TrigonometryQuiz class"""
    quiz = MathQuiz()
    
    # Try accessing without unlock
    print("Jadvalni ko'rishga urinish (maxfiy bo'lim):")
    print(quiz.get_trigonometry_table())
    print()
    
    # Unlock with correct code
    print("Kod bilan ochish: 0107")
    if quiz.unlock_hidden_section("0107"):
        print("✅ Maxfiy bo'lim ochildi!")
        print()
        
        # Show table
        print(quiz.get_trigonometry_table())
        print()
        
        # Generate a single question
        question = quiz.generate_question(45, "sin")
        print(f"Savol: {question['question_text']}")
        for i, opt in enumerate(question['options']):
            print(f"  {question['option_letters'][i]}) {opt}")
        print()
        
        # Generate quiz session
        print("🎯 10 ta savoldan iborat kichik test:")
        quiz_session = quiz.generate_quiz_session(10)
        for i, q in enumerate(quiz_session, 1):
            print(f"{i}. {q['question_text']}")
    else:
        print("❌ Kod noto'g'ri!")


def full_quiz_example():
    """Complete quiz example with all features"""
    quiz = MathQuiz()
    
    print("=" * 80)
    print("🔒 MAXFIY BO'LIM - TRIGONOMETRIYA TESTI")
    print("=" * 80)
    print()
    
    # Unlock
    print("📝 Kod kiriting (0107):")
    code = "0107"
    if not quiz.unlock_hidden_section(code):
        print("❌ Kod noto'g'ri!")
        return
    
    print("✅ Maxfiy bo'lim ochildi!")
    print()
    
    # Start quiz
    print("📊 Quiz boshlanyapti...")
    quiz_questions = quiz.generate_quiz_session(5)  # 5 ta savol
    
    if not quiz_questions:
        print("❌ Quiz yaratib bo'lmadi")
        return
    
    print(f"Jami savollar: {len(quiz_questions)}")
    print()
    
    # Process each question
    for i in range(len(quiz_questions)):
        question = quiz.get_next_question()
        if not question:
            break
        
        progress = quiz.get_current_progress()
        print(f"\n{'='*60}")
        print(f"📍 {progress['message']}")
        print(f"{'='*60}")
        print(f"❓ {question['question_text']}")
        print()
        
        # Show options
        for j, option in enumerate(question['options']):
            print(f"   {question['option_letters'][j]}) {option}")
        
        # Simulate answer (randomly select one)
        selected_index = random.randint(0, len(question['options']) - 1)
        selected_option = question['options'][selected_index]
        
        print(f"\n📌 Tanlangan javob: {question['option_letters'][selected_index]}) {selected_option}")
        
        # Check answer
        is_correct, feedback = quiz.check_answer(question, selected_index)
        print(f"   {feedback}")
    
    # Show results
    print(f"\n{'='*60}")
    print("📈 TEST NATIJALARI")
    print(f"{'='*60}")
    
    results = quiz.get_quiz_results()
    print(f"✅ To'g'ri: {results['correct']}/{results['total_questions']}")
    print(f"❌ Noto'g'ri: {results['wrong']}/{results['total_questions']}")
    print(f"📊 Foiz: {results['percentage']}%")
    print(f"🏆 Baho: {results['rating']}")
    
    # Statistics
    print(f"\n{'='*60}")
    print("📊 BATAFSIL STATISTIKA")
    print(f"{'='*60}")
    
    stats = quiz.get_detailed_statistics()
    
    if stats['by_function']:
        print("\n🔢 FUNKSIYALAR BO'YICHA:")
        for func, data in sorted(stats['by_function'].items()):
            percentage = (data['correct'] / data['total']) * 100 if data['total'] > 0 else 0
            print(f"   {func.upper()}: {data['correct']}/{data['total']} ({percentage:.1f}%)")
    
    if stats['by_angle']:
        print("\n📐 GRADUSLARI BO'YICHA (TOP 5):")
        sorted_angles = sorted(stats['by_angle'].items(), 
                              key=lambda x: (x[1]['correct']/x[1]['total'], x[1]['total']), 
                              reverse=True)[:5]
        for angle, data in sorted_angles:
            percentage = (data['correct'] / data['total']) * 100 if data['total'] > 0 else 0
            print(f"   {angle}°: {data['correct']}/{data['total']} ({percentage:.1f}%)")
    
    print()


if __name__ == "__main__":
    # Run both examples
    example_usage()
    print("\n" + "="*80 + "\n")
    full_quiz_example()

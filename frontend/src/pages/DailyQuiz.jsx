import React, { useState, useEffect } from 'react';

// Sub-component: A single quiz card
const QuizCard = ({ questionData, questionNum, totalQuestions, onAnswer }) => {
  const [selectedOption, setSelectedOption] = useState(null);
  const [isRevealed, setIsRevealed] = useState(false);

  const handleOptionClick = (index) => {
    if (isRevealed) return;
    setSelectedOption(index);
    setIsRevealed(true);
    
    // Pass the truthy/falsy value after a short delay for UX
    setTimeout(() => {
      onAnswer(index === questionData.correct_index);
      setSelectedOption(null);
      setIsRevealed(false);
    }, 1500);
  };

  return (
    <div className="glass-card" style={{ maxWidth: '600px', margin: '0 auto', animation: 'slideUp 0.4s ease-out' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        <span>Daily Quiz</span>
        <span>Question {questionNum} of {totalQuestions}</span>
      </div>
      
      <h2 style={{ fontSize: '1.5rem', marginBottom: '2rem', color: 'var(--text-main)', lineHeight: '1.4' }}>
        {questionData.question}
      </h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {questionData.options.map((option, index) => {
          let btnStyle = {
            padding: '1rem 1.5rem',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '2px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '12px',
            color: 'var(--text-main)',
            fontSize: '1.1rem',
            textAlign: 'left',
            cursor: isRevealed ? 'default' : 'pointer',
            transition: 'all 0.2s',
            fontWeight: 500
          };

          if (isRevealed) {
            if (index === questionData.correct_index) {
              btnStyle.background = 'rgba(16, 185, 129, 0.2)';
              btnStyle.borderColor = '#10b981'; // Green for correct
            } else if (index === selectedOption) {
              btnStyle.background = 'rgba(239, 68, 68, 0.2)';
              btnStyle.borderColor = '#ef4444'; // Red for wrong selected
            }
          }

          return (
            <button 
              key={index} 
              style={btnStyle}
              onClick={() => handleOptionClick(index)}
              onMouseEnter={(e) => {
                if (!isRevealed) {
                  e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                  e.target.style.borderColor = 'var(--accent-cyan)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isRevealed && index !== selectedOption) {
                  e.target.style.background = 'rgba(255, 255, 255, 0.05)';
                  e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                }
              }}
            >
              <span style={{ marginRight: '1rem', color: 'var(--text-muted)' }}>{String.fromCharCode(65 + index)}</span>
              {option}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default function DailyQuiz() {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [quizComplete, setQuizComplete] = useState(false);
  const [loading, setLoading] = useState(true);
  const [streak, setStreak] = useState(0);

  // Helper to get formatted date string "YYYY-MM-DD"
  const getTodayStr = () => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  };

  useEffect(() => {
    fetch('/data/questions.json')
      .then(res => res.json())
      .then(allQuestions => {
        // Date-seed logic: day of year
        const today = new Date();
        const start = new Date(today.getFullYear(), 0, 0);
        const diff = today - start;
        const oneDay = 1000 * 60 * 60 * 24;
        const dayOfYear = Math.floor(diff / oneDay);
        
        // Select 3 questions deterministically based on date
        const startIndex = (dayOfYear * 3) % Math.max(1, allQuestions.length - 3);
        const selected = allQuestions.slice(startIndex, startIndex + 3);
        
        // Ensure we handle edge cases where array is too short
        if (selected.length < 3) {
            setQuestions(allQuestions.slice(0, 3));
        } else {
            setQuestions(selected);
        }

        // Load streak
        const stored = localStorage.getItem('ipl_quiz_state');
        if (stored) {
          const parsed = JSON.parse(stored);
          setStreak(parsed.streak || 0);

          // If they already completed it today
          if (parsed.lastPlayedDate === getTodayStr()) {
             setQuizComplete(true);
             setScore(parsed.lastScore || 0);
          }
        }
        
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load quiz", err);
        setLoading(false);
      });
  }, []);

  const handleAnswer = (isCorrect) => {
    if (isCorrect) {
      setScore(prev => prev + 1);
    }
    
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      finishQuiz(isCorrect ? score + 1 : score);
    }
  };

  const finishQuiz = (finalScore) => {
    setScore(finalScore);
    setQuizComplete(true);

    const todayStr = getTodayStr();
    
    let currentStreak = 0;
    const stored = localStorage.getItem('ipl_quiz_state');
    
    if (stored) {
       const parsed = JSON.parse(stored);
       const lastDate = parsed.lastPlayedDate;
       const yesterday = new Date();
       yesterday.setDate(yesterday.getDate() - 1);
       const yyyy = yesterday.getFullYear();
       const mm = String(yesterday.getMonth() + 1).padStart(2, '0');
       const dd = String(yesterday.getDate()).padStart(2, '0');
       const yesterdayStr = `${yyyy}-${mm}-${dd}`;

       if (lastDate === yesterdayStr) {
          currentStreak = parsed.streak + 1;
       } else if (lastDate === todayStr) {
          currentStreak = parsed.streak; // Already played today? shouldn't happen, but safe
       } else {
          currentStreak = 1; // Missed a day
       }
    } else {
       currentStreak = 1; // First time playing
    }

    setStreak(currentStreak);
    
    localStorage.setItem('ipl_quiz_state', JSON.stringify({
      lastPlayedDate: todayStr,
      streak: currentStreak,
      lastScore: finalScore
    }));
  };

  const handleShare = () => {
    const text = `🏏 IPL Daily Quiz\nScore: ${score}/3\n🔥 Streak: ${streak} days\nPlay now at Daily IPL Analytics!`;
    navigator.clipboard.writeText(text);
    alert('Result copied to clipboard!');
  };

  if (loading) {
    return (
      <div className="dashboard-content" style={{ textAlign: 'center', paddingTop: '4rem', color: 'var(--text-muted)' }}>
        Loading quiz...
      </div>
    );
  }

  return (
    <div className="dashboard-content" style={{ paddingTop: '2rem' }}>
      <h1 className="section-title">🧠 <span className="text-gradient">Daily IPL Quiz</span></h1>
      
      {!quizComplete && questions.length > 0 && (
         <QuizCard 
           questionData={questions[currentIndex]} 
           questionNum={currentIndex + 1} 
           totalQuestions={questions.length} 
           onAnswer={handleAnswer} 
         />
      )}

      {quizComplete && (
         <div className="glass-card" style={{ maxWidth: '500px', margin: '0 auto', textAlign: 'center', padding: '3rem 2rem', animation: 'slideUp 0.5s ease-out' }}>
            <h2 style={{ fontSize: '2.2rem', marginBottom: '1rem', color: 'var(--accent-cyan)' }}>Quiz Complete!</h2>
            
            <div style={{ display: 'flex', justifyContent: 'center', gap: '3rem', margin: '2.5rem 0' }}>
               <div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>Your Score</div>
                  <div style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--text-main)', lineHeight: '1' }}>{score}<span style={{fontSize:'1.5rem', color: 'var(--text-muted)'}}>/3</span></div>
               </div>
               <div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>Current Streak</div>
                  <div style={{ fontSize: '3rem', fontWeight: 800, color: '#f59e0b', lineHeight: '1', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>{streak} <span style={{fontSize:'2rem'}}>🔥</span></div>
               </div>
            </div>

            <button onClick={handleShare} className="premium-button" style={{ 
               width: '100%', 
               padding: '1rem', 
               fontSize: '1.2rem', 
               display: 'flex', 
               alignItems: 'center', 
               justifyContent: 'center', 
               gap: '0.75rem',
               background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))',
               color: 'white',
               boxShadow: '0 4px 15px rgba(6, 182, 212, 0.4)'
            }}>
               <i>📋</i> Share Result
            </button>
            <p style={{ marginTop: '1.5rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Check back tomorrow for 3 new questions!</p>
         </div>
      )}
    </div>
  );
}

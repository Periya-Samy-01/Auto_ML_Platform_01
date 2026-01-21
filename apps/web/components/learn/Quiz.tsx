"use client";

import { useState } from "react";
import {
    CheckCircle2,
    XCircle,
    Trophy,
    RotateCcw,
    ChevronRight,
    Play,
    Clock,
    HelpCircle,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { submitQuiz } from "@/lib/api/learning";
import type { QuizQuestion, QuizResult } from "@/types/learning";

interface QuizProps {
    topicId: string;
    topicTitle: string;
    questions: QuizQuestion[];
    onComplete?: (result: QuizResult) => void;
}

export function Quiz({ topicId, topicTitle, questions, onComplete }: QuizProps) {
    const [started, setStarted] = useState(false);
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [answers, setAnswers] = useState<Record<string, string>>({});
    const [result, setResult] = useState<QuizResult | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const [showResults, setShowResults] = useState(false);

    const question = questions[currentQuestion];
    const selectedAnswer = answers[question?.id];
    const progress = ((currentQuestion + 1) / questions.length) * 100;
    const allAnswered = Object.keys(answers).length === questions.length;

    const handleStart = () => {
        setStarted(true);
    };

    const handleSelectAnswer = (optionId: string) => {
        if (showResults) return; // Can't change answers after submission
        setAnswers((prev) => ({
            ...prev,
            [question.id]: optionId,
        }));
    };

    const handleNext = () => {
        if (currentQuestion < questions.length - 1) {
            setCurrentQuestion((prev) => prev + 1);
        }
    };

    const handlePrev = () => {
        if (currentQuestion > 0) {
            setCurrentQuestion((prev) => prev - 1);
        }
    };

    const handleSubmit = async () => {
        try {
            setSubmitting(true);
            const quizResult = await submitQuiz(topicId, answers);
            setResult(quizResult);
            setShowResults(true);
            setCurrentQuestion(0); // Go back to first question to show results
            onComplete?.(quizResult);
        } catch (err) {
            console.error("Failed to submit quiz:", err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleRetry = () => {
        setAnswers({});
        setResult(null);
        setShowResults(false);
        setCurrentQuestion(0);
        setStarted(true); // Stay started for retry
    };

    // Show intro screen before starting
    if (!started) {
        return (
            <Card className="hover:border-primary/50 transition-colors">
                <CardContent className="p-8">
                    <div className="flex items-center gap-6">
                        {/* Quiz Icon */}
                        <div className="w-16 h-16 rounded-2xl bg-yellow-500/10 flex items-center justify-center flex-shrink-0">
                            <Trophy className="w-8 h-8 text-yellow-400" />
                        </div>

                        {/* Quiz Info */}
                        <div className="flex-1">
                            <h3 className="text-xl font-semibold mb-2">{topicTitle} Quiz</h3>
                            <p className="text-muted-foreground mb-4">
                                Test your knowledge and earn your completion badge!
                            </p>

                            {/* Stats */}
                            <div className="flex items-center gap-6 text-sm text-muted-foreground">
                                <div className="flex items-center gap-2">
                                    <HelpCircle className="w-4 h-4" />
                                    <span>{questions.length} questions</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Clock className="w-4 h-4" />
                                    <span>~{Math.ceil(questions.length * 0.5)} min</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <CheckCircle2 className="w-4 h-4" />
                                    <span>70% to pass</span>
                                </div>
                            </div>
                        </div>

                        {/* Start Button */}
                        <Button onClick={handleStart} size="lg" className="gap-2">
                            <Play className="w-4 h-4" />
                            Start Quiz
                        </Button>
                    </div>
                </CardContent>
            </Card>
        );
    }

    // Show results summary
    if (showResults && result) {
        return (
            <Card className="border-2 border-primary/30">
                <CardContent className="p-8">
                    <div className="text-center">
                        {/* Result Icon */}
                        <div
                            className={`w-20 h-20 rounded-full mx-auto mb-6 flex items-center justify-center ${result.passed
                                ? "bg-green-500/20 text-green-400"
                                : "bg-yellow-500/20 text-yellow-400"
                                }`}
                        >
                            <Trophy className="w-10 h-10" />
                        </div>

                        {/* Score */}
                        <h2 className="text-3xl font-bold mb-2">
                            {result.score} / {result.total}
                        </h2>
                        <p className="text-lg text-muted-foreground mb-2">
                            {result.percentage.toFixed(0)}% Correct
                        </p>

                        {/* Status Badge */}
                        <Badge
                            className={`text-sm mb-6 ${result.passed
                                ? "bg-green-500/20 text-green-400 border-green-500/30"
                                : "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
                                }`}
                        >
                            {result.passed ? "Quiz Passed! 🎉" : "Keep Learning!"}
                        </Badge>

                        {/* Message */}
                        <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                            {result.passed
                                ? `Congratulations! You've mastered the ${topicTitle} fundamentals.`
                                : `You need 70% to pass. Review the lessons and try again!`}
                        </p>

                        {/* Actions */}
                        <div className="flex items-center justify-center gap-4">
                            <Button variant="outline" onClick={handleRetry} className="gap-2">
                                <RotateCcw className="w-4 h-4" />
                                Retry Quiz
                            </Button>
                            <Button
                                onClick={() => setShowResults(false)}
                                className="gap-2"
                            >
                                Review Answers
                                <ChevronRight className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="border-2 border-primary/30">
            <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">
                        {topicTitle} Quiz
                    </CardTitle>
                    <Badge variant="outline">
                        Question {currentQuestion + 1} of {questions.length}
                    </Badge>
                </div>
                <Progress value={progress} className="h-2 mt-4" />
            </CardHeader>

            <CardContent className="space-y-6">
                {/* Question */}
                <div>
                    <h3 className="text-lg font-medium mb-4">{question.question}</h3>

                    {/* Options */}
                    <div className="space-y-3">
                        {question.options.map((option) => {
                            const isSelected = selectedAnswer === option.id;
                            const isCorrect =
                                showResults && result?.correct_answers[question.id] === option.id;
                            const isWrong =
                                showResults && isSelected && !isCorrect;

                            let optionClass =
                                "w-full p-4 rounded-lg border text-left transition-all ";

                            if (showResults) {
                                if (isCorrect) {
                                    optionClass +=
                                        "border-green-500/50 bg-green-500/10 text-green-400";
                                } else if (isWrong) {
                                    optionClass +=
                                        "border-red-500/50 bg-red-500/10 text-red-400";
                                } else {
                                    optionClass +=
                                        "border-border bg-transparent text-muted-foreground";
                                }
                            } else {
                                if (isSelected) {
                                    optionClass +=
                                        "border-primary bg-primary/10 text-foreground";
                                } else {
                                    optionClass +=
                                        "border-border bg-transparent text-muted-foreground hover:border-primary/50 hover:bg-primary/5";
                                }
                            }

                            return (
                                <button
                                    key={option.id}
                                    onClick={() => handleSelectAnswer(option.id)}
                                    disabled={showResults}
                                    className={optionClass}
                                >
                                    <div className="flex items-center gap-3">
                                        <div
                                            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${showResults && isCorrect
                                                ? "border-green-500 bg-green-500"
                                                : showResults && isWrong
                                                    ? "border-red-500 bg-red-500"
                                                    : isSelected
                                                        ? "border-primary bg-primary"
                                                        : "border-muted-foreground"
                                                }`}
                                        >
                                            {showResults && isCorrect && (
                                                <CheckCircle2 className="w-4 h-4 text-white" />
                                            )}
                                            {showResults && isWrong && (
                                                <XCircle className="w-4 h-4 text-white" />
                                            )}
                                            {!showResults && isSelected && (
                                                <div className="w-2 h-2 rounded-full bg-white" />
                                            )}
                                        </div>
                                        <span>{option.text}</span>
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Navigation */}
                <div className="flex items-center justify-between pt-4 border-t border-border">
                    <Button
                        variant="ghost"
                        onClick={handlePrev}
                        disabled={currentQuestion === 0}
                    >
                        Previous
                    </Button>

                    <div className="flex items-center gap-2">
                        {/* Question dots */}
                        {questions.map((q, idx) => (
                            <button
                                key={q.id}
                                onClick={() => setCurrentQuestion(idx)}
                                className={`w-2.5 h-2.5 rounded-full transition-colors ${idx === currentQuestion
                                    ? "bg-primary"
                                    : answers[q.id]
                                        ? showResults
                                            ? result?.correct_answers[q.id] === answers[q.id]
                                                ? "bg-green-500"
                                                : "bg-red-500"
                                            : "bg-primary/50"
                                        : "bg-muted"
                                    }`}
                            />
                        ))}
                    </div>

                    {currentQuestion === questions.length - 1 ? (
                        showResults ? (
                            <Button onClick={() => setShowResults(true)}>
                                View Results
                            </Button>
                        ) : (
                            <Button
                                onClick={handleSubmit}
                                disabled={!allAnswered || submitting}
                            >
                                {submitting ? "Submitting..." : "Submit Quiz"}
                            </Button>
                        )
                    ) : (
                        <Button onClick={handleNext} disabled={!selectedAnswer}>
                            Next
                        </Button>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}

"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
    ArrowLeft,
    BookOpen,
    Target,
    TrendingUp,
    Layers,
    Wrench,
    BarChart3,
    Brain,
    Lightbulb,
    Clock,
    CheckCircle2,
    Circle,
    Play,
    Trophy,
    LucideIcon,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { getTopic } from "@/lib/api/learning";
import type { TopicDetail, Lesson, QuizResult } from "@/types/learning";
import { Quiz } from "@/components/learn/Quiz";

// Icon mapping for topics
const iconMap: Record<string, LucideIcon> = {
    BookOpen,
    Target,
    TrendingUp,
    Layers,
    Wrench,
    BarChart3,
    Brain,
    Lightbulb,
};

// Difficulty badge colors
const difficultyColors: Record<string, string> = {
    BEGINNER: "bg-green-500/20 text-green-400 border-green-500/30",
    INTERMEDIATE: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    ADVANCED: "bg-red-500/20 text-red-400 border-red-500/30",
};

export default function TopicDetailPage() {
    const params = useParams();
    const router = useRouter();
    const topicId = params.topicId as string;

    const [topic, setTopic] = useState<TopicDetail | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [quizCompleted, setQuizCompleted] = useState(false);

    useEffect(() => {
        const fetchTopic = async () => {
            try {
                setLoading(true);
                const data = await getTopic(topicId);
                setTopic(data);
            } catch (err) {
                console.error("Failed to fetch topic:", err);
                setError("Failed to load topic. Please try again.");
            } finally {
                setLoading(false);
            }
        };

        if (topicId) {
            fetchTopic();
        }
    }, [topicId]);

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="h-8 w-48 bg-muted animate-pulse rounded" />
                <div className="h-24 bg-muted animate-pulse rounded-xl" />
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {[...Array(8)].map((_, i) => (
                        <div key={i} className="h-32 bg-muted animate-pulse rounded-xl" />
                    ))}
                </div>
            </div>
        );
    }

    if (error || !topic) {
        return (
            <div className="flex flex-col items-center justify-center py-16">
                <p className="text-muted-foreground mb-4">{error || "Topic not found"}</p>
                <Button variant="outline" onClick={() => router.push("/dashboard/learn")}>
                    Back to Learning Center
                </Button>
            </div>
        );
    }

    const TopicIcon = iconMap[topic.icon] || BookOpen;

    return (
        <div className="space-y-6">
            {/* Back Navigation */}
            <Link
                href="/dashboard/learn"
                className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
            >
                <ArrowLeft className="w-4 h-4" />
                Back to Learning Center
            </Link>

            {/* Topic Header */}
            <Card className="border-0 bg-gradient-to-r from-card to-card/50">
                <CardContent className="p-6">
                    <div className="flex items-start gap-6">
                        {/* Topic Icon */}
                        <div
                            className={`w-16 h-16 rounded-2xl ${topic.bg_color} flex items-center justify-center flex-shrink-0`}
                        >
                            <TopicIcon className={`w-8 h-8 ${topic.color}`} />
                        </div>

                        {/* Topic Info */}
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3 mb-2">
                                <h1 className="text-2xl font-bold">{topic.title}</h1>
                                {topic.difficulty && (
                                    <Badge
                                        variant="outline"
                                        className={difficultyColors[topic.difficulty]}
                                    >
                                        {topic.difficulty}
                                    </Badge>
                                )}
                                {topic.is_completed && (
                                    <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                                        <Trophy className="w-3 h-3 mr-1" />
                                        Completed
                                    </Badge>
                                )}
                            </div>

                            <p className="text-muted-foreground mb-4">{topic.description}</p>

                            {/* Progress & Stats */}
                            <div className="flex items-center gap-6">
                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <BookOpen className="w-4 h-4" />
                                    <span>
                                        {topic.completed_lessons} / {topic.lesson_count} lessons
                                    </span>
                                </div>
                                {topic.estimated_minutes && (
                                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                        <Clock className="w-4 h-4" />
                                        <span>{topic.estimated_minutes} min</span>
                                    </div>
                                )}
                            </div>

                            {/* Progress Bar */}
                            <div className="mt-4">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm text-muted-foreground">Progress</span>
                                    <span className="text-sm font-medium">
                                        {topic.progress_percentage}%
                                    </span>
                                </div>
                                <Progress value={topic.progress_percentage} className="h-2" />
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Lessons Grid */}
            <div>
                <h2 className="text-xl font-semibold mb-4">Lessons</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {topic.lessons.map((lesson, index) => (
                        <LessonCard
                            key={lesson.id}
                            lesson={lesson}
                            topicId={topicId}
                            lessonNumber={index + 1}
                        />
                    ))}
                </div>
            </div>

            {/* Quiz Section (if available) */}
            {topic.quiz && topic.quiz.length > 0 && (
                <div>
                    <h2 className="text-xl font-semibold mb-4">Quiz</h2>
                    <Quiz
                        topicId={topicId}
                        topicTitle={topic.title}
                        questions={topic.quiz}
                        onComplete={(result: QuizResult) => {
                            setQuizCompleted(true);
                            // Refresh topic to update quiz_passed status
                            getTopic(topicId).then(setTopic);
                        }}
                    />
                </div>
            )}
        </div>
    );
}

// Lesson Card Component
function LessonCard({
    lesson,
    topicId,
    lessonNumber,
}: {
    lesson: Lesson;
    topicId: string;
    lessonNumber: number;
}) {
    return (
        <Link href={`/dashboard/learn/${topicId}/${lesson.id}`}>
            <Card
                className={`h-full hover:border-primary/50 transition-all cursor-pointer group ${lesson.is_completed ? "border-green-500/30 bg-green-500/5" : ""
                    }`}
            >
                <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                            <div
                                className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-medium ${lesson.is_completed
                                    ? "bg-green-500/20 text-green-400"
                                    : "bg-muted text-muted-foreground"
                                    }`}
                            >
                                {lesson.is_completed ? (
                                    <CheckCircle2 className="w-4 h-4" />
                                ) : (
                                    lessonNumber
                                )}
                            </div>
                            <div className="flex-1 min-w-0">
                                <CardTitle className="text-base font-medium line-clamp-1">
                                    {lesson.title}
                                </CardTitle>
                            </div>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                        {lesson.description}
                    </p>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Clock className="w-3 h-3" />
                            <span>{lesson.estimated_minutes} min</span>
                        </div>
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                            <Play className="w-4 h-4 text-primary" />
                        </div>
                    </div>
                </CardContent>
            </Card>
        </Link>
    );
}

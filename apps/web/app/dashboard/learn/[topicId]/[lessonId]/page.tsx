"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import {
    ArrowLeft,
    ArrowRight,
    Clock,
    CheckCircle2,
    BookOpen,
} from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getLesson, completeLesson, getTopic } from "@/lib/api/learning";
import type { LessonDetail, TopicDetail } from "@/types/learning";

export default function LessonPage() {
    const params = useParams();
    const router = useRouter();
    const topicId = params.topicId as string;
    const lessonId = params.lessonId as string;

    const [lesson, setLesson] = useState<LessonDetail | null>(null);
    const [topic, setTopic] = useState<TopicDetail | null>(null);
    const [loading, setLoading] = useState(true);
    const [completing, setCompleting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Find next/prev lessons
    const currentIndex = topic?.lessons.findIndex((l) => l.id === lessonId) ?? -1;
    const prevLesson = currentIndex > 0 ? topic?.lessons[currentIndex - 1] : null;
    const nextLesson =
        currentIndex >= 0 && currentIndex < (topic?.lessons.length ?? 0) - 1
            ? topic?.lessons[currentIndex + 1]
            : null;

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [lessonData, topicData] = await Promise.all([
                    getLesson(topicId, lessonId),
                    getTopic(topicId),
                ]);
                setLesson(lessonData);
                setTopic(topicData);
            } catch (err) {
                console.error("Failed to fetch lesson:", err);
                setError("Failed to load lesson. Please try again.");
            } finally {
                setLoading(false);
            }
        };

        if (topicId && lessonId) {
            fetchData();
        }
    }, [topicId, lessonId]);

    const handleMarkComplete = async () => {
        if (!lesson) return;

        try {
            setCompleting(true);
            await completeLesson(topicId, lessonId);
            // Refresh topic to get updated progress
            const updatedTopic = await getTopic(topicId);
            setTopic(updatedTopic);
            // Update lesson state
            setLesson((prev) => (prev ? { ...prev, is_completed: true } : prev));
        } catch (err) {
            console.error("Failed to mark lesson complete:", err);
        } finally {
            setCompleting(false);
        }
    };

    if (loading) {
        return (
            <div className="space-y-6 max-w-4xl mx-auto">
                <div className="h-8 w-48 bg-muted animate-pulse rounded" />
                <div className="h-64 bg-muted animate-pulse rounded-xl" />
                <div className="space-y-4">
                    <div className="h-4 bg-muted animate-pulse rounded w-full" />
                    <div className="h-4 bg-muted animate-pulse rounded w-3/4" />
                    <div className="h-4 bg-muted animate-pulse rounded w-5/6" />
                </div>
            </div>
        );
    }

    if (error || !lesson || !topic) {
        return (
            <div className="flex flex-col items-center justify-center py-16">
                <p className="text-muted-foreground mb-4">
                    {error || "Lesson not found"}
                </p>
                <Button
                    variant="outline"
                    onClick={() => router.push(`/dashboard/learn/${topicId}`)}
                >
                    Back to Topic
                </Button>
            </div>
        );
    }

    const isCompleted =
        topic.lessons.find((l) => l.id === lessonId)?.is_completed ?? false;

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Back Navigation */}
            <Link
                href={`/dashboard/learn/${topicId}`}
                className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
            >
                <ArrowLeft className="w-4 h-4" />
                Back to {topic.title}
            </Link>

            {/* Lesson Header */}
            <div className="flex items-start justify-between gap-4">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <Badge variant="outline" className="text-xs">
                            Lesson {lesson.order}
                        </Badge>
                        {isCompleted && (
                            <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                                <CheckCircle2 className="w-3 h-3 mr-1" />
                                Completed
                            </Badge>
                        )}
                    </div>
                    <h1 className="text-2xl font-bold mb-2">{lesson.title}</h1>
                    <p className="text-muted-foreground">{lesson.description}</p>
                </div>

                <div className="flex items-center gap-2 text-sm text-muted-foreground flex-shrink-0">
                    <Clock className="w-4 h-4" />
                    <span>{lesson.estimated_minutes} min</span>
                </div>
            </div>

            {/* Lesson Content */}
            <Card>
                <CardContent className="p-8">
                    {lesson.content ? (
                        <div className="prose prose-invert max-w-none prose-headings:text-foreground prose-p:text-muted-foreground prose-strong:text-foreground prose-code:text-primary prose-code:bg-primary/10 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-pre:bg-card prose-pre:border prose-pre:border-border">
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                    // Style headings
                                    h2: ({ children }) => (
                                        <h2 className="text-xl font-bold text-foreground mt-8 mb-4 pb-2 border-b border-border">
                                            {children}
                                        </h2>
                                    ),
                                    h3: ({ children }) => (
                                        <h3 className="text-lg font-semibold text-foreground mt-6 mb-3">
                                            {children}
                                        </h3>
                                    ),
                                    // Style paragraphs
                                    p: ({ children }) => (
                                        <p className="text-muted-foreground leading-relaxed mb-4">
                                            {children}
                                        </p>
                                    ),
                                    // Style lists
                                    ul: ({ children }) => (
                                        <ul className="list-disc list-inside space-y-2 mb-4 text-muted-foreground">
                                            {children}
                                        </ul>
                                    ),
                                    ol: ({ children }) => (
                                        <ol className="list-decimal list-inside space-y-2 mb-4 text-muted-foreground">
                                            {children}
                                        </ol>
                                    ),
                                    li: ({ children }) => (
                                        <li className="text-muted-foreground">{children}</li>
                                    ),
                                    // Style code blocks
                                    pre: ({ children }) => (
                                        <div className="my-4">
                                            {children}
                                        </div>
                                    ),
                                    code: ({ className, children, node, ...props }) => {
                                        const match = /language-(\w+)/.exec(className || "");
                                        const codeString = String(children).replace(/\n$/, "");

                                        // Check if this is a code block: has language class OR contains newlines (multi-line)
                                        const isCodeBlock = match || className?.includes("language-") || codeString.includes("\n");

                                        if (isCodeBlock) {
                                            return (
                                                <SyntaxHighlighter
                                                    style={atomDark}
                                                    language={match?.[1] || "text"}
                                                    PreTag="div"
                                                    customStyle={{
                                                        margin: 0,
                                                        borderRadius: "0.5rem",
                                                        padding: "1rem",
                                                        fontSize: "0.875rem",
                                                        border: "1px solid hsl(var(--border))",
                                                        background: "#1a1a2e",
                                                    }}
                                                    wrapLines={true}
                                                    wrapLongLines={true}
                                                >
                                                    {codeString}
                                                </SyntaxHighlighter>
                                            );
                                        }

                                        // Inline code
                                        return (
                                            <code className="text-primary bg-primary/10 px-1.5 py-0.5 rounded font-mono text-sm">
                                                {children}
                                            </code>
                                        );
                                    },
                                    // Style blockquotes
                                    blockquote: ({ children }) => (
                                        <blockquote className="border-l-4 border-primary/50 pl-4 italic text-muted-foreground my-4">
                                            {children}
                                        </blockquote>
                                    ),
                                    // Style tables
                                    table: ({ children }) => (
                                        <div className="overflow-x-auto my-4">
                                            <table className="w-full border-collapse border border-border">
                                                {children}
                                            </table>
                                        </div>
                                    ),
                                    th: ({ children }) => (
                                        <th className="border border-border bg-muted/50 px-4 py-2 text-left font-semibold">
                                            {children}
                                        </th>
                                    ),
                                    td: ({ children }) => (
                                        <td className="border border-border px-4 py-2 text-muted-foreground">
                                            {children}
                                        </td>
                                    ),
                                    // Style strong/bold
                                    strong: ({ children }) => (
                                        <strong className="text-foreground font-semibold">
                                            {children}
                                        </strong>
                                    ),
                                }}
                            >
                                {lesson.content}
                            </ReactMarkdown>
                        </div>
                    ) : (
                        <div className="text-center py-16">
                            <BookOpen className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                            <h3 className="text-lg font-medium mb-2">Content Coming Soon</h3>
                            <p className="text-muted-foreground max-w-md mx-auto">
                                This lesson's content is being prepared. Check back soon for the
                                full tutorial!
                            </p>
                        </div>
                    )}

                    {/* Key Points */}
                    {lesson.key_points && lesson.key_points.length > 0 && (
                        <div className="mt-8 p-4 rounded-lg bg-primary/5 border border-primary/10">
                            <h3 className="font-semibold mb-3">Key Points</h3>
                            <ul className="space-y-2">
                                {lesson.key_points.map((point, index) => (
                                    <li
                                        key={index}
                                        className="flex items-start gap-2 text-sm text-muted-foreground"
                                    >
                                        <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                                        <span>{point}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-border">
                {/* Previous Lesson */}
                <div>
                    {prevLesson ? (
                        <Link href={`/dashboard/learn/${topicId}/${prevLesson.id}`}>
                            <Button variant="ghost" className="gap-2">
                                <ArrowLeft className="w-4 h-4" />
                                {prevLesson.title}
                            </Button>
                        </Link>
                    ) : (
                        <div />
                    )}
                </div>

                {/* Mark Complete / Next */}
                <div className="flex items-center gap-3">
                    {!isCompleted && (
                        <Button
                            onClick={handleMarkComplete}
                            disabled={completing}
                            className="gap-2"
                        >
                            {completing ? (
                                "Marking..."
                            ) : (
                                <>
                                    <CheckCircle2 className="w-4 h-4" />
                                    Mark as Complete
                                </>
                            )}
                        </Button>
                    )}

                    {nextLesson ? (
                        <Link href={`/dashboard/learn/${topicId}/${nextLesson.id}`}>
                            <Button variant="outline" className="gap-2">
                                Next: {nextLesson.title}
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                        </Link>
                    ) : (
                        <Link href={`/dashboard/learn/${topicId}`}>
                            <Button variant="outline" className="gap-2">
                                Back to Topic
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                        </Link>
                    )}
                </div>
            </div>
        </div>
    );
}
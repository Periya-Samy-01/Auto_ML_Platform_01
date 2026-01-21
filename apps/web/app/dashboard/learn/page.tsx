"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  BookOpen,
  Target,
  TrendingUp,
  Layers,
  Wrench,
  BarChart3,
  Brain,
  Lightbulb,
  CheckCircle2,
  LucideIcon,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { getTopics } from "@/lib/api/learning";
import type { TopicListItem } from "@/types/learning";

// Icon mapping
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

// Fallback topics for when API is unavailable
const fallbackTopics = [
  {
    id: "ml-basics",
    title: "ML Basics",
    description: "Introduction to machine learning concepts and terminology",
    icon: "BookOpen",
    color: "text-blue-400",
    bg_color: "bg-blue-500/10",
    lesson_count: 7,
    completed_lessons: 0,
    progress_percentage: 0,
    is_completed: false,
  },
  {
    id: "classification",
    title: "Classification",
    description: "Learn to predict categories and classes from data",
    icon: "Target",
    color: "text-green-400",
    bg_color: "bg-green-500/10",
    lesson_count: 11,
    completed_lessons: 0,
    progress_percentage: 0,
    is_completed: false,
  },
  {
    id: "regression",
    title: "Regression",
    description: "Predict continuous values and understand relationships",
    icon: "TrendingUp",
    color: "text-purple-400",
    bg_color: "bg-purple-500/10",
    lesson_count: 9,
    completed_lessons: 0,
    progress_percentage: 0,
    is_completed: false,
  },
  {
    id: "clustering",
    title: "Clustering",
    description: "Group similar data points without labeled examples",
    icon: "Layers",
    color: "text-orange-400",
    bg_color: "bg-orange-500/10",
    lesson_count: 5,
    completed_lessons: 0,
    progress_percentage: 0,
    is_completed: false,
  },
  {
    id: "feature-engineering",
    title: "Feature Engineering",
    description: "Transform raw data into features for better models",
    icon: "Wrench",
    color: "text-cyan-400",
    bg_color: "bg-cyan-500/10",
    lesson_count: 7,
    completed_lessons: 0,
    progress_percentage: 0,
    is_completed: false,
  },
  {
    id: "model-evaluation",
    title: "Model Evaluation",
    description: "Metrics and techniques to assess model performance",
    icon: "BarChart3",
    color: "text-pink-400",
    bg_color: "bg-pink-500/10",
    lesson_count: 6,
    completed_lessons: 0,
    progress_percentage: 0,
    is_completed: false,
  },
  {
    id: "neural-networks",
    title: "Neural Networks",
    description: "Introduction to deep learning fundamentals",
    icon: "Brain",
    color: "text-red-400",
    bg_color: "bg-red-500/10",
    lesson_count: 14,
    completed_lessons: 0,
    progress_percentage: 0,
    is_completed: false,
  },
  {
    id: "best-practices",
    title: "Best Practices",
    description: "Tips and tricks for successful ML projects",
    icon: "Lightbulb",
    color: "text-yellow-400",
    bg_color: "bg-yellow-500/10",
    lesson_count: 4,
    completed_lessons: 0,
    progress_percentage: 0,
    is_completed: false,
  },
];

export default function LearnPage() {
  const [topics, setTopics] = useState<TopicListItem[]>(fallbackTopics as TopicListItem[]);
  const [loading, setLoading] = useState(true);
  const [totalCompleted, setTotalCompleted] = useState(0);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const data = await getTopics();
        setTopics(data.topics);
        setTotalCompleted(data.completed_topics);
      } catch (err) {
        console.error("Failed to fetch topics, using fallback:", err);
        // Keep fallback topics
      } finally {
        setLoading(false);
      }
    };

    fetchTopics();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Learning Center</h2>
          <p className="text-muted-foreground mt-1">
            Master machine learning concepts with interactive tutorials
          </p>
        </div>
        {totalCompleted > 0 && (
          <Badge variant="outline" className="text-sm">
            {totalCompleted} / {topics.length} completed
          </Badge>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {topics.map((topic) => (
          <TopicCard key={topic.id} topic={topic} loading={loading} />
        ))}
      </div>
    </div>
  );
}

function TopicCard({
  topic,
  loading,
}: {
  topic: TopicListItem;
  loading: boolean;
}) {
  const TopicIcon = iconMap[topic.icon] || BookOpen;

  return (
    <Link href={`/dashboard/learn/${topic.id}`}>
      <Card
        className={`h-full hover:border-primary/50 transition-colors cursor-pointer group ${topic.is_completed ? "border-green-500/30" : ""
          }`}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div
              className={`w-12 h-12 rounded-xl ${topic.bg_color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}
            >
              <TopicIcon className={`w-6 h-6 ${topic.color}`} />
            </div>
            {topic.is_completed && (
              <CheckCircle2 className="w-5 h-5 text-green-400" />
            )}
          </div>
          <CardTitle className="text-lg">{topic.title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-3">
            {topic.description}
          </p>

          {/* Progress */}
          {topic.progress_percentage > 0 && !topic.is_completed && (
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-muted-foreground">
                  {topic.completed_lessons} / {topic.lesson_count} lessons
                </span>
                <span className="text-xs font-medium">
                  {topic.progress_percentage}%
                </span>
              </div>
              <Progress value={topic.progress_percentage} className="h-1" />
            </div>
          )}

          {/* Lesson count */}
          {topic.progress_percentage === 0 && (
            <p className="text-xs text-muted-foreground">
              {topic.lesson_count} lessons
            </p>
          )}

          {/* Completed state */}
          {topic.is_completed && (
            <p className="text-xs text-green-400">
              ✓ All {topic.lesson_count} lessons completed
            </p>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}

import { Globe } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import {
  Background,
  Controls,
  Handle,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Edge,
  type Node,
  type NodeProps,
} from "reactflow";
import "reactflow/dist/style.css";
import { useRoadmapProgress } from "../hooks/useRoadmapProgress";
import type { CourseRoadmap } from "../types/chat";

// ---------------------------------------------------------------------------
// Location state coming from ChatPage
// ---------------------------------------------------------------------------
interface RoadmapLocationState {
  course?: CourseRoadmap;
  /** If true, the roadmap is still being generated — connect WS. */
  generating?: boolean;
}

interface CourseNodeData {
  label: string;
  description?: string;
}

interface SectionNodeData {
  label: string;
  description?: string;
}

interface TopicNodeData {
  label: string;
  description?: string;
  duration?: string;
  links?: string[];
  status: "not_started" | "in_progress" | "completed";
}

function CourseNode({ data }: NodeProps<CourseNodeData>) {
  return (
    <div className="rf-card rf-card-course">
      <Handle type="source" position={Position.Bottom} isConnectable={false} />
      <div className="rf-card-title">{data.label}</div>
      {data.description && (
        <div className="rf-card-subtitle">{data.description}</div>
      )}
    </div>
  );
}

function SectionNode({ data }: NodeProps<SectionNodeData>) {
  return (
    <div className="rf-card rf-card-section">
      <Handle type="target" position={Position.Top} isConnectable={false} />
      <Handle type="source" position={Position.Bottom} isConnectable={false} />
      <div className="rf-card-title">{data.label}</div>
      {data.description && (
        <div className="rf-card-subtitle">{data.description}</div>
      )}
    </div>
  );
}

function TopicNode({ data }: NodeProps<TopicNodeData>) {
  return (
    <div className="rf-card rf-card-topic">
      <Handle type="target" position={Position.Top} isConnectable={false} />
      <div className="rf-card-topic-header">
        <div className="rf-card-title rf-card-title--small">{data.label}</div>
        <span className={`rf-card-status rf-card-status--${data.status}`}>
          {data.status === "not_started" && "Not started"}
          {data.status === "in_progress" && "In progress"}
          {data.status === "completed" && "Completed"}
        </span>
      </div>
      {data.description && (
        <div className="rf-card-subtitle rf-card-subtitle--muted">
          {data.description}
        </div>
      )}
      {data.duration && <div className="rf-card-meta">{data.duration}</div>}
      {data.links && data.links.length > 0 && (
        <div
          className="rf-card-links"
          style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}
        >
          {data.links.map((link, index) => (
            <a
              key={index}
              href={link}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Globe />
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

const nodeTypes = {
  course: CourseNode,
  section: SectionNode,
  topic: TopicNode,
} as const;

// ---------------------------------------------------------------------------
// Graph builder
// ---------------------------------------------------------------------------
function buildGraph(course: CourseRoadmap) {
  const nodes: Node[] = [];
  const edges: Edge[] = [];

  const courseNodeId = `course-${course.id}`;
  nodes.push({
    id: courseNodeId,
    position: { x: 0, y: 0 },
    data: {
      label: course.title,
      description: course.objective,
    } satisfies CourseNodeData,
    type: "course",
  });

  const sectionSpacingX = 420;
  const baseSectionY = 150;

  course.sections.forEach((section, sectionIndex) => {
    const sectionId = `section-${section.id}`;
    const sectionX = sectionIndex * sectionSpacingX;
    const sectionY = baseSectionY;

    nodes.push({
      id: sectionId,
      position: { x: sectionX, y: sectionY },
      data: {
        label: section.title,
        description: section.description,
      } satisfies SectionNodeData,
      type: "section",
    });

    edges.push({
      id: `${courseNodeId}-${sectionId}`,
      source: courseNodeId,
      target: sectionId,
      animated: true,
    });

    const topicSpacingY = 130;
    const topicBaseY = sectionY + 80;

    section.topics.forEach((topic, topicIndex) => {
      const topicId = `topic-${topic.id}`;
      const topicY = topicBaseY + topicIndex * topicSpacingY;

      nodes.push({
        id: topicId,
        position: { x: sectionX, y: topicY },
        data: {
          label: topic.title,
          description: topic.description,
          duration: topic.estimatedDuration,
          status: topic.status,
          links: topic.links,
        } satisfies TopicNodeData,
        type: "topic",
      });

      edges.push({
        id: `${sectionId}-${topicId}`,
        source: sectionId,
        target: topicId,
      });
    });
  });

  return { nodes, edges };
}

// ---------------------------------------------------------------------------
// Progress step emojis
// ---------------------------------------------------------------------------
const STEP_EMOJIS: Record<string, string> = {
  analysing_answers: "\u{1F50D}",
  researching: "\u{1F4DA}",
  planning: "\u{1F5FA}\uFE0F",
  generating_roadmap: "\u{2728}",
  done: "\u{2705}",
  failed: "\u{274C}",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export function RoadmapPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();
  const locState = location.state as RoadmapLocationState | null;

  // The course can come from navigation state OR from the WS once generated
  const [course, setCourse] = useState<CourseRoadmap | null>(
    locState?.course ?? null,
  );
  const isGenerating = locState?.generating === true && !course;

  // Connect to WS only when the roadmap is still being generated
  const progress = useRoadmapProgress(isGenerating ? (id ?? null) : null);

  // When the WS delivers the completed roadmap, store it.
  // Using queueMicrotask to avoid synchronous setState in effect body.
  useEffect(() => {
    if (progress.status === "completed" && progress.roadmap) {
      queueMicrotask(() => setCourse(progress.roadmap));
    }
  }, [progress.status, progress.roadmap]);

  // Build React-Flow graph whenever the course changes
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    if (!course) return { nodes: [], edges: [] };
    return buildGraph(course);
  }, [course]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Sync React Flow state when the computed graph changes
  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  // -----------------------------------------------------------------------
  // Generating / loading state
  // -----------------------------------------------------------------------
  if (!course) {
    const emoji = STEP_EMOJIS[progress.step] ?? "";

    return (
      <div className="roadmap-page">
        <header className="roadmap-header">
          <button
            type="button"
            className="roadmap-back-button"
            onClick={() => navigate("/chat")}
          >
            &larr; Back to chat
          </button>
          <h1 className="roadmap-title">
            {progress.status === "error"
              ? "Something went wrong"
              : "Curating your roadmap"}
          </h1>
        </header>

        <main className="roadmap-loading">
          {progress.status === "error" ? (
            <div className="roadmap-error">
              <p>{progress.error ?? "An unexpected error occurred."}</p>
              <button
                type="button"
                className="roadmap-back-button"
                onClick={() => navigate("/chat")}
              >
                Return to chat
              </button>
            </div>
          ) : (
            <div className="roadmap-progress">
              {/* Progress bar */}
              <div className="roadmap-progress-bar-track">
                <div
                  className="roadmap-progress-bar-fill"
                  style={{ width: `${progress.progressPct}%` }}
                />
              </div>

              <p className="roadmap-progress-pct">
                {progress.progressPct}% complete
              </p>

              {/* Step detail */}
              <p className="roadmap-progress-detail">
                {emoji} {progress.detail || "Preparing\u2026"}
              </p>

              {/* Animated dots to show activity */}
              <div className="roadmap-progress-dots">
                <span className="roadmap-dot" />
                <span className="roadmap-dot" />
                <span className="roadmap-dot" />
              </div>
            </div>
          )}
        </main>
      </div>
    );
  }

  // -----------------------------------------------------------------------
  // Roadmap ready
  // -----------------------------------------------------------------------
  return (
    <div className="roadmap-page">
      <header className="roadmap-header">
        <button
          type="button"
          className="roadmap-back-button"
          onClick={() => navigate("/chat")}
        >
          &larr; Back to chat
        </button>
        <div className="roadmap-header-main">
          <h1 className="roadmap-title">{course.title}</h1>
          <p className="roadmap-subtitle">{course.objective}</p>
        </div>
        <div className="roadmap-header-meta">
          <span className="roadmap-level">{course.level.toUpperCase()}</span>
          {course.totalEstimatedDuration && (
            <span className="roadmap-duration">
              {course.totalEstimatedDuration}
            </span>
          )}
          <span className="roadmap-id">ID: {id ?? course.id}</span>
        </div>
      </header>

      <main className="roadmap-content">
        <section className="roadmap-overview">
          <h2>Overview</h2>
          <p>{course.description}</p>
        </section>
        <div className="roadmap-flow-wrapper">
          {nodes && (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              nodeTypes={nodeTypes}
              defaultEdgeOptions={{
                animated: false,
                type: "smoothstep",
                style: {
                  stroke: "rgba(189, 232, 245, 0.9)",
                  strokeWidth: 2,
                },
              }}
              fitView
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              zoomOnScroll
              zoomOnPinch
            >
              <Background gap={18} size={1} />
              <Controls showInteractive={true} />
            </ReactFlow>
          )}
        </div>
      </main>
    </div>
  );
}

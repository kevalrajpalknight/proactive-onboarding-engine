import { useMemo } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
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
    type NodeProps
} from 'reactflow'
import 'reactflow/dist/style.css'
import type { CourseRoadmap } from '../types/chat'

interface RoadmapLocationState {
  course?: CourseRoadmap
}

interface CourseNodeData {
  label: string
  description?: string
}

interface SectionNodeData {
  label: string
  description?: string
}

interface TopicNodeData {
  label: string
  description?: string
  duration?: string
  status: 'not_started' | 'in_progress' | 'completed'
}

function CourseNode({ data }: NodeProps<CourseNodeData>) {
  return (
    <div className="rf-card rf-card-course">
      <Handle type="source" position={Position.Bottom} isConnectable={false} />
      <div className="rf-card-title">{data.label}</div>
      {data.description && <div className="rf-card-subtitle">{data.description}</div>}
    </div>
  )
}

function SectionNode({ data }: NodeProps<SectionNodeData>) {
  return (
    <div className="rf-card rf-card-section">
      <Handle type="target" position={Position.Top} isConnectable={false} />
      <Handle type="source" position={Position.Bottom} isConnectable={false} />
      <div className="rf-card-title">{data.label}</div>
      {data.description && <div className="rf-card-subtitle">{data.description}</div>}
    </div>
  )
}

function TopicNode({ data }: NodeProps<TopicNodeData>) {
  return (
    <div className="rf-card rf-card-topic">
      <Handle type="target" position={Position.Top} isConnectable={false} />
      <div className="rf-card-topic-header">
        <div className="rf-card-title rf-card-title--small">{data.label}</div>
        <span className={`rf-card-status rf-card-status--${data.status}`}>
          {data.status === 'not_started' && 'Not started'}
          {data.status === 'in_progress' && 'In progress'}
          {data.status === 'completed' && 'Completed'}
        </span>
      </div>
      {data.description && <div className="rf-card-subtitle rf-card-subtitle--muted">{data.description}</div>}
      {data.duration && <div className="rf-card-meta">{data.duration}</div>}
    </div>
  )
}

const nodeTypes = {
  course: CourseNode,
  section: SectionNode,
  topic: TopicNode,
} as const

export function RoadmapPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const location = useLocation()
  const state = location.state as RoadmapLocationState | null

  const course = state?.course

  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    if (!course) {
      return { nodes: [], edges: [] }
    }

    const nodes: Node[] = []
    const edges: Edge[] = []

    const courseNodeId = `course-${course.id}`
    nodes.push({
      id: courseNodeId,
      position: { x: 0, y: 0 },
      data: {
        label: course.title,
        description: course.objective,
      } satisfies CourseNodeData,
      type: 'course',
    })

    const sectionSpacingX = 420
    const baseSectionY = 150

    course.sections.forEach((section, sectionIndex) => {
      const sectionId = `section-${section.id}`
      const sectionX = sectionIndex * sectionSpacingX
      const sectionY = baseSectionY

      nodes.push({
        id: sectionId,
        position: { x: sectionX, y: sectionY },
        data: {
          label: section.title,
          description: section.description,
        } satisfies SectionNodeData,
        type: 'section',
      })

      edges.push({
        id: `${courseNodeId}-${sectionId}`,
        source: courseNodeId,
        target: sectionId,
        animated: true,
      })

      const topicSpacingY = 130
      const topicBaseY = sectionY + 80

      section.topics.forEach((topic, topicIndex) => {
        const topicId = `topic-${topic.id}`
        const topicY = topicBaseY + topicIndex * topicSpacingY

        nodes.push({
          id: topicId,
          position: { x: sectionX, y: topicY },
          data: {
            label: topic.title,
            description: topic.description,
            duration: topic.estimatedDuration,
            status: topic.status,
          } satisfies TopicNodeData,
          type: 'topic',
        })

        edges.push({
          id: `${sectionId}-${topicId}`,
          source: sectionId,
          target: topicId,
        })
      })
    })

    return { nodes, edges }
  }, [course])

  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  if (!course) {
    return (
      <div className="roadmap-page">
        <header className="roadmap-header">
          <button
            type="button"
            className="roadmap-back-button"
            onClick={() => navigate('/chat')}
          >
            ← Back to chat
          </button>
          <h1 className="roadmap-title">Roadmap not found</h1>
          <p className="roadmap-subtitle">
            We could not find the tailored roadmap for this session.
          </p>
        </header>
      </div>
    )
  }

  return (
    <div className="roadmap-page">
      <header className="roadmap-header">
        <button
          type="button"
          className="roadmap-back-button"
          onClick={() => navigate('/chat')}
        >
          ← Back to chat
        </button>
        <div className="roadmap-header-main">
          <h1 className="roadmap-title">{course.title}</h1>
          <p className="roadmap-subtitle">{course.objective}</p>
        </div>
        <div className="roadmap-header-meta">
          <span className="roadmap-level">{course.level.toUpperCase()}</span>
          {course.totalEstimatedDuration && (
            <span className="roadmap-duration">{course.totalEstimatedDuration}</span>
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
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            defaultEdgeOptions={{
              animated: false,
              type: 'smoothstep',
              style: {
                stroke: 'rgba(189, 232, 245, 0.9)',
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
        </div>
      </main>
    </div>
  )
}

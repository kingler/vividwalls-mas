# Enhanced BDI Model Integration Plan

## Overview

This document outlines a comprehensive plan for enhancing the Belief-Desire-Intention (BDI) model in our agent architecture to better align with business objectives and incorporate additional elements such as goals, plans, and a reward system.

## Current BDI Model

The current implementation focuses on:
- **Beliefs**: What agents know about the world
- **Desires**: What agents want to achieve
- **Intentions**: What agents are committed to doing

## Enhanced BDI Model

Based on feedback, we will extend this model to include:

1. **Goals**: Business-aligned objectives that agents should pursue
   - Strategic goals (long-term)
   - Tactical goals (medium-term)
   - Operational goals (short-term)

2. **Plans**: Structured approaches to achieve goals
   - Step-by-step procedures
   - Decision points
   - Success criteria

3. **Reward System**: Merit-based incentive mechanism
   - Point accumulation for successful tasks
   - Point reduction for failures
   - Performance tracking over time

4. **Business Alignment**: Explicit connection to Vivid Walls objectives
   - Art sales objectives
   - Print-on-demand service requirements
   - Size variations and product specifications

## Implementation Strategy

### 1. Neo4j Data Model Extensions

#### 1.1 Goal Nodes

```cypher
CREATE (g:Goal {
  id: "goal-123",
  name: "Increase Art Sales",
  description: "Increase monthly art sales by 15%",
  type: "strategic", // strategic, tactical, operational
  priority: 0.9,
  deadline: datetime("2025-06-30"),
  metrics: ["monthly_sales", "conversion_rate"],
  business_unit: "sales"
})
```

#### 1.2 Plan Nodes

```cypher
CREATE (p:Plan {
  id: "plan-456",
  name: "Summer Art Promotion",
  description: "Promote summer-themed art collections",
  steps: ["identify_summer_art", "create_promotions", "launch_campaign"],
  success_criteria: "15% increase in summer art sales",
  resources_required: ["marketing_budget", "design_time"],
  estimated_duration: "30 days"
})
```

#### 1.3 Reward System Nodes

```cypher
CREATE (r:RewardSystem {
  id: "reward-789",
  name: "Sales Performance Rewards",
  description: "Merit points for sales performance",
  point_scale: "1-100",
  threshold_for_success: 70,
  reset_period: "monthly"
})
```

#### 1.4 Business Objective Nodes

```cypher
CREATE (b:BusinessObjective {
  id: "obj-123",
  name: "Expand Print-on-Demand Services",
  description: "Increase POD service offerings by 25%",
  target_date: datetime("2025-12-31"),
  kpis: ["service_variety", "production_capacity", "customer_satisfaction"],
  owner: "operations"
})
```

#### 1.5 Relationships

```cypher
// Connect goals to business objectives
MATCH (g:Goal), (b:BusinessObjective {id: "obj-123"})
CREATE (g)-[:ALIGNS_WITH]->(b)

// Connect goals to plans
MATCH (g:Goal), (p:Plan {id: "plan-456"})
CREATE (g)-[:IMPLEMENTED_BY]->(p)

// Connect plans to actions
MATCH (p:Plan), (a:Action {id: "action-789"})
CREATE (p)-[:INCLUDES]->(a)

// Connect agents to reward systems
MATCH (agent:Agent), (r:RewardSystem)
CREATE (agent)-[:PARTICIPATES_IN {current_points: 0, history: []}]->(r)

// Connect agents to goals
MATCH (agent:Agent), (g:Goal)
CREATE (agent)-[:PURSUES {priority: 0.8, assigned_date: datetime()}]->(g)
```

### 2. Reasoning Service Enhancements

#### 2.1 Goal Management

```typescript
/**
 * Goal management functions for the reasoning service
 */
class GoalManager {
  /**
   * Assign goals to an agent based on business objectives
   */
  async assignGoals(agentId: string): Promise<void> {
    // Implementation
  }

  /**
   * Check goal alignment with beliefs
   */
  async checkGoalBeliefAlignment(agentId: string, goalId: string): Promise<boolean> {
    // Implementation
  }

  /**
   * Track goal achievement progress
   */
  async trackGoalProgress(agentId: string, goalId: string): Promise<number> {
    // Implementation
  }
}
```

#### 2.2 Plan Execution

```typescript
/**
 * Plan execution functions for the reasoning service
 */
class PlanExecutor {
  /**
   * Select appropriate plan based on goals and context
   */
  async selectPlan(agentId: string, goalId: string): Promise<string> {
    // Implementation
  }

  /**
   * Execute plan steps sequentially
   */
  async executePlanStep(agentId: string, planId: string, stepIndex: number): Promise<boolean> {
    // Implementation
  }

  /**
   * Monitor plan execution progress
   */
  async monitorPlanProgress(agentId: string, planId: string): Promise<number> {
    // Implementation
  }
}
```

#### 2.3 Reward Processing

```typescript
/**
 * Reward processing functions for the reasoning service
 */
class RewardProcessor {
  /**
   * Calculate merit points based on task performance
   */
  async calculateMeritPoints(agentId: string, taskId: string, success: boolean): Promise<number> {
    // Implementation
  }

  /**
   * Update agent's reward history
   */
  async updateRewardHistory(agentId: string, points: number, reason: string): Promise<void> {
    // Implementation
  }

  /**
   * Use reward history to influence decision making
   */
  async applyRewardInfluence(agentId: string, decisionContext: any): Promise<any> {
    // Implementation
  }
}
```

### 3. Enhanced Reasoning Cycle

The current reasoning cycle will be extended to include:

1. **Goal Evaluation**
   - Assess current goals against business objectives
   - Prioritize goals based on importance and urgency
   - Adjust goals based on changing business needs

2. **Plan Selection**
   - Choose appropriate plans to achieve goals
   - Evaluate plan feasibility based on resources and constraints
   - Prepare for plan execution

3. **Plan Execution**
   - Execute plan steps sequentially
   - Monitor progress and handle exceptions
   - Adjust execution based on feedback

4. **Reward Calculation**
   - Evaluate task performance against success criteria
   - Calculate merit points based on performance
   - Update agent's reward history

5. **Learning and Adaptation**
   - Use reward history to influence future decisions
   - Adapt behavior based on past successes and failures
   - Improve performance over time

### 4. Flowise Integration Extensions

#### 4.1 Goal-Oriented Agents

```typescript
/**
 * Convert Neo4j agent with goals to Flowise agent
 */
public async convertNeo4jAgentWithGoalsToFlowiseAgent(neo4jAgentId: string): Promise<FlowiseAgent> {
  try {
    // Get Neo4j agent
    const neo4jAgent = await this.getNeo4jAgentById(neo4jAgentId);
    
    // Get agent beliefs, desires, intentions, and actions
    const beliefs = await this.reasoningService.getAgentBeliefs(neo4jAgentId);
    const desires = await this.reasoningService.getAgentDesires(neo4jAgentId);
    const intentions = await this.reasoningService.getAgentIntentions(neo4jAgentId);
    const actions = await this.reasoningService.getAgentActions(neo4jAgentId);
    
    // Get agent goals and plans
    const goals = await this.reasoningService.getAgentGoals(neo4jAgentId);
    const plans = await this.reasoningService.getAgentPlans(neo4jAgentId);
    
    // Get agent reward history
    const rewards = await this.reasoningService.getAgentRewards(neo4jAgentId);

    // Create Flowise agent with enhanced BDI model
    const flowiseAgent: FlowiseAgent = {
      name: neo4jAgent.name,
      description: neo4jAgent.description || `Agent created from Neo4j agent ${neo4jAgentId}`,
      metadata: {
        neo4jAgentId,
        type: neo4jAgent.type || 'enhanced-bdi',
        domain: neo4jAgent.domain || [],
        beliefs: beliefs.map(b => ({
          id: b.belief.id,
          content: b.belief.content,
          confidence: b.confidence,
          origin: b.origin
        })),
        desires: desires.map(d => ({
          id: d.desire.id,
          content: d.desire.content,
          priority: d.priority,
          motivation: d.motivation
        })),
        intentions: intentions.map(i => ({
          id: i.intention.id,
          content: i.intention.content,
          commitment: i.commitment
        })),
        actions: actions.map(a => ({
          id: a.action.id,
          content: a.action.content,
          status: a.status,
          priority: a.priority
        })),
        goals: goals.map(g => ({
          id: g.goal.id,
          name: g.goal.name,
          description: g.goal.description,
          type: g.goal.type,
          priority: g.priority,
          deadline: g.goal.deadline
        })),
        plans: plans.map(p => ({
          id: p.plan.id,
          name: p.plan.name,
          description: p.plan.description,
          steps: p.plan.steps,
          success_criteria: p.plan.success_criteria,
          progress: p.progress
        })),
        rewards: {
          current_points: rewards.current_points,
          history: rewards.history
        }
      }
    };

    return flowiseAgent;
  } catch (error) {
    this.logger.error(`Failed to convert Neo4j agent to Flowise agent: ${(error as Error).message}`);
    throw error;
  }
}
```

#### 4.2 Plan Execution Support

```typescript
/**
 * Execute a plan step through Flowise
 */
public async executePlanStepViaFlowise(neo4jAgentId: string, planId: string, stepIndex: number): Promise<any> {
  try {
    // Get the plan step details
    const planStep = await this.reasoningService.getPlanStep(neo4jAgentId, planId, stepIndex);
    
    // Execute the step via Flowise
    const result = await this.executeFlowiseAgentFromNeo4j(neo4jAgentId, {
      action: "execute_plan_step",
      plan_id: planId,
      step_index: stepIndex,
      step_details: planStep
    });
    
    // Update plan progress in Neo4j
    await this.reasoningService.updatePlanStepStatus(neo4jAgentId, planId, stepIndex, result.status);
    
    return result;
  } catch (error) {
    this.logger.error(`Failed to execute plan step via Flowise: ${(error as Error).message}`);
    throw error;
  }
}
```

#### 4.3 Reward System Integration

```typescript
/**
 * Process task result and update reward points
 */
public async processTaskResultAndUpdateRewards(neo4jAgentId: string, taskId: string, result: any): Promise<number> {
  try {
    // Evaluate task success
    const success = this.evaluateTaskSuccess(taskId, result);
    
    // Calculate merit points
    const points = await this.reasoningService.calculateMeritPoints(neo4jAgentId, taskId, success);
    
    // Update reward history
    await this.reasoningService.updateRewardHistory(neo4jAgentId, points, 
      success ? `Successfully completed task ${taskId}` : `Failed to complete task ${taskId}`);
    
    // Return the points awarded/deducted
    return points;
  } catch (error) {
    this.logger.error(`Failed to process task result and update rewards: ${(error as Error).message}`);
    throw error;
  }
}
```

## Implementation Phases

### Phase 1: Data Model Enhancement (Week 1-2)

1. **Schema Design**
   - Design Neo4j schema extensions for goals, plans, and rewards
   - Define relationships between new and existing entities
   - Document the enhanced data model

2. **Database Updates**
   - Implement Neo4j schema changes
   - Create migration scripts for existing data
   - Add constraints and indexes for performance

3. **Sample Data Creation**
   - Create sample goals aligned with Vivid Walls business
   - Define example plans for common scenarios
   - Set up initial reward system parameters

### Phase 2: Reasoning Service Updates (Week 3-4)

1. **Goal Management**
   - Implement goal assignment functionality
   - Develop goal-belief alignment checking
   - Create goal progress tracking

2. **Plan Execution**
   - Build plan selection algorithms
   - Implement step-by-step execution
   - Develop progress monitoring

3. **Reward Processing**
   - Create merit point calculation logic
   - Implement reward history tracking
   - Develop decision influence mechanisms

### Phase 3: Flowise Bridge Extensions (Week 5-6)

1. **Agent Conversion**
   - Update agent conversion to include goals and plans
   - Enhance metadata structure for new elements
   - Ensure backward compatibility

2. **Execution Enhancement**
   - Extend execution to support plan steps
   - Implement context-aware execution
   - Add reward feedback loops

3. **Synchronization**
   - Develop bidirectional sync for new elements
   - Implement change detection and propagation
   - Ensure data consistency

### Phase 4: Testing and Validation (Week 7-8)

1. **Unit Testing**
   - Test individual components
   - Verify data model integrity
   - Validate calculation accuracy

2. **Integration Testing**
   - Test end-to-end workflows
   - Verify Neo4j-Flowise communication
   - Validate reward system behavior

3. **Business Scenario Testing**
   - Test with Vivid Walls specific scenarios
   - Validate business alignment
   - Measure performance against objectives

## Business Context Integration

### Vivid Walls Specific Elements

#### Art Sales Goals

```cypher
CREATE (g:Goal {
  id: "goal-art-sales-1",
  name: "Increase Limited Edition Sales",
  description: "Boost sales of limited edition prints by 20%",
  type: "tactical",
  priority: 0.9,
  deadline: datetime("2025-06-30"),
  metrics: ["limited_edition_sales", "average_order_value"],
  business_unit: "sales"
})
```

#### Print-on-Demand Plans

```cypher
CREATE (p:Plan {
  id: "plan-pod-1",
  name: "Optimize Print Production",
  description: "Streamline print-on-demand production process",
  steps: [
    "analyze_current_workflow",
    "identify_bottlenecks",
    "implement_automation",
    "measure_improvements"
  ],
  success_criteria: "25% reduction in production time",
  resources_required: ["production_analysis", "automation_tools"],
  estimated_duration: "45 days"
})
```

#### Product Specifications

```cypher
CREATE (ps:ProductSpec {
  id: "spec-1",
  name: "Canvas Print Specifications",
  sizes: ["8x10", "11x14", "16x20", "24x36"],
  materials: ["standard canvas", "premium canvas"],
  framing_options: ["none", "floating frame", "traditional frame"],
  pricing_tiers: ["standard", "premium", "luxury"],
  production_time: "3-5 business days"
})

// Connect to relevant goals and plans
MATCH (g:Goal {id: "goal-art-sales-1"}), (ps:ProductSpec {id: "spec-1"})
CREATE (g)-[:REFERENCES]->(ps)
```

#### Customer Interaction Patterns

```cypher
CREATE (ci:CustomerInteraction {
  id: "interaction-1",
  type: "inquiry_handling",
  description: "Process for handling customer inquiries about art sizes",
  steps: [
    "acknowledge_inquiry",
    "provide_size_information",
    "suggest_appropriate_options",
    "follow_up_on_decision"
  ],
  response_time_target: "2 hours",
  success_metrics: ["customer_satisfaction", "conversion_rate"]
})

// Connect to agents responsible for customer interaction
MATCH (agent:Agent {role: "customer_service"}), (ci:CustomerInteraction {id: "interaction-1"})
CREATE (agent)-[:HANDLES]->(ci)
```

## Reward System Details

### Merit Point Calculation

```typescript
/**
 * Calculate merit points based on task performance
 */
function calculateMeritPoints(task, result) {
  // Base points for the task
  const basePoints = task.difficulty * 10;
  
  // Success multiplier
  const successMultiplier = result.success ? 1.0 : -0.5;
  
  // Quality factor (0.0 to 1.0)
  const qualityFactor = result.quality || 0.7;
  
  // Time efficiency factor
  const timeEfficiency = Math.min(task.expected_time / result.actual_time, 1.5);
  
  // Calculate total points
  const totalPoints = basePoints * successMultiplier * qualityFactor * timeEfficiency;
  
  return Math.round(totalPoints);
}
```

### Reward Thresholds

| Level | Points Required | Benefits |
|-------|----------------|----------|
| Novice | 0-100 | Basic task access |
| Apprentice | 101-500 | Intermediate task access |
| Expert | 501-1000 | Advanced task access, priority resource allocation |
| Master | 1001+ | Full autonomy, resource allocation control, mentoring capabilities |

### Reward Influence on Decision Making

```typescript
/**
 * Adjust decision weights based on reward history
 */
function adjustDecisionWeights(agent, decision) {
  // Get agent's current level
  const level = getAgentLevel(agent.rewards.current_points);
  
  // Base weights
  let weights = {
    risk_taking: 0.5,
    innovation: 0.5,
    thoroughness: 0.5,
    speed: 0.5
  };
  
  // Adjust based on level
  switch(level) {
    case 'Novice':
      weights.risk_taking = 0.2;
      weights.thoroughness = 0.8;
      break;
    case 'Apprentice':
      weights.risk_taking = 0.4;
      weights.innovation = 0.6;
      break;
    case 'Expert':
      weights.risk_taking = 0.6;
      weights.speed = 0.7;
      break;
    case 'Master':
      weights.risk_taking = 0.8;
      weights.innovation = 0.9;
      break;
  }
  
  // Apply weights to decision
  return applyWeightsToDecision(decision, weights);
}
```

## Questions for Consideration

1. How should we prioritize goals when they conflict?
2. What specific metrics should be used to calculate merit points for Vivid Walls tasks?
3. How frequently should the reward system be updated?
4. What business-specific constraints should be incorporated into plans?
5. How should we handle plan failures or adjustments?
6. How can we ensure that agent goals remain aligned with changing business objectives?
7. What mechanisms should be in place for human oversight of the reward system?
8. How can we measure the effectiveness of the enhanced BDI model?

## Next Steps

1. Review this plan with stakeholders
2. Prioritize implementation phases
3. Assign resources to each phase
4. Develop detailed technical specifications
5. Begin implementation with data model enhancements
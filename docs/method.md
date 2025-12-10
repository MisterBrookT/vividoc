┌─────────────────────┐
│    Planner Agent     │
│  (structure + logic) │
└──────────┬──────────┘
           ↓
     Document Spec
 (self-contained plan)
           ↓
       Exec Input
┌─────────────────────┐
│     Exec Agent       │
│ (text + interactive  │
│    code generation)  │
└──────────┬──────────┘
           ↓
      Renderable Code
           ↓
┌─────────────────────┐
│      Eval Agent      │
│ (coherence + runtime│
│      correctness)    │
└──────────┬──────────┘
     feedback-loop
       (Exec only)

Minimal Example:

###  input 
what is π? 

###  Planner Agent
input: the topic

step1: generate knowledge units (ku) from the topic (sub-outline)
step2: generate text description （self-contained description）
step3: generate interactivte description (self-contained description)

output: document spec.
e.g.

```json
{
  "topic": "What is π?",
  "knowledge_units": [
    {
      "id": "ku1",
      "unit_content": "π represents the ratio between a circle's circumference and its diameter.",
      "text_description": "This section explains that every circle has two essential measurements—its circumference, which is the distance around the circle, and its diameter, which is the distance across the circle through its center—and introduces the idea that the ratio between these two values is always the same regardless of the circle's size. The reader should gain an intuitive understanding of why mathematicians define π as this ratio and how this definition connects the geometry of any circle to a universal mathematical constant.",
      "interaction_description": "In this part, the reader can adjust the radius of a circle using a slider, and as the radius changes, the visualization updates the circle in real time while recalculating and displaying the circumference, the diameter, and the resulting ratio between them, allowing the reader to see directly that the ratio stays roughly the same even when the size of the circle varies."
    },

    {
      "id": "ku2",
      "unit_content": "The value of π is constant for all circles regardless of size.",
      "text_description": "This section clarifies that π does not change when the size of the circle changes, emphasizing that both tiny circles and very large circles follow the same geometric relationship between circumference and diameter. The goal is for the reader to understand that π is a universal constant, not a property of any specific circle, and that this consistency across scale is one reason π is so fundamental in mathematics.",
      "interaction_description": "This part does not include active user interaction; instead, the system presents several circles of different sizes placed side by side, each labeled with its circumference and diameter, so the reader can visually compare them and observe that although the individual values differ, the ratio between circumference and diameter remains effectively identical across all circles."
    },

    {
      "id": "ku3",
      "unit_content": "We can experimentally approximate π by measuring circumference and diameter.",
      "text_description": "This section discusses how π can be approximated in real-life scenarios by physically measuring an object's diameter and the distance it travels when rolled out one full revolution, which corresponds to its circumference, and it introduces the concept of empirical measurement as a way to approximate mathematical constants when an exact value is difficult or impossible to write down. The reader should understand that real measurements involve small inaccuracies, but the resulting ratio still tends to approach π.",
      "interaction_description": "In this part, the reader chooses an object from a dropdown menu, each with a different known diameter, and then drags the selected object along a straight line to simulate rolling it, causing the system to measure the distance the object covers as an approximation of its circumference and to compute the ratio between the measured circumference and known diameter, showing how this hands-on process yields a value close to π despite natural measurement variations."
    },

    {
      "id": "ku4",
      "unit_content": "π also appears in geometry, trigonometry, and many physical formulas.",
      "text_description": "This section explains that π is not only related to circles but also appears in many important areas of mathematics and science, such as the formulas for the area and circumference of a circle, the shapes of waves described by trigonometric functions, and the behavior of oscillations, rotations, and other physical phenomena, giving the reader a broader sense of π’s importance as a unifying constant across diverse domains.",
      "interaction_description": "This part contains no interactive component; instead, the system displays a collection of well-known formulas and diagrams from geometry, trigonometry, and physics where π plays a central role, presenting them clearly so the reader can recognize how frequently this constant appears in mathematical and scientific contexts."
    }
  ]
}
```

### Exec Agent
渐进式的生成text和interactivte code
1) write text: 根据text_descrption生成文字内容。
2) write code : 根据interaction_description生成交互代码。
3) check bug: 执行代码，判断错误，修复代码。
### Eval agent
1） 根据text整体的overall fluency反馈给code agent
2） 交互片段是否正常渲染。反馈给code agent

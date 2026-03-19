#!/usr/bin/env bun
/**
 * Scene Detection Script
 * 
 * Analyzes content to identify the most likely scene type for image generation.
 * Used by smart-image-generator skill to automatically detect user intent.
 */

import { readFile } from 'node:fs/promises';
import { extname } from 'node:path';

type SceneType = 'cover' | 'flowchart' | 'poster' | 'diagram' | 'infographic' | 'social' | 'slide';

type SceneScore = {
  scene: SceneType;
  score: number;
  confidence: 'high' | 'medium' | 'low';
  reasons: string[];
};

const SCENE_KEYWORDS: Record<SceneType, string[]> = {
  cover: [
    'cover', 'header', 'hero image', 'article', 'post', 'blog',
    'title', 'headline', 'frontmatter', 'metadata'
  ],
  flowchart: [
    'flowchart', 'flow chart', 'process', 'workflow', 'procedure',
    'step', 'first', 'then', 'next', 'if', 'else', 'when', 'decide',
    'decision', 'branch', 'loop', 'sequence'
  ],
  poster: [
    'poster', 'promotion', 'promotional', 'event', 'conference',
    'workshop', 'webinar', 'announce', 'announcement', 'launch',
    'sale', 'discount', 'offer', 'register', 'ticket'
  ],
  diagram: [
    'diagram', 'architecture', 'system design', 'components',
    'structure', 'schema', 'model', 'blueprint'
  ],
  infographic: [
    'infographic', 'data', 'chart', 'statistics', 'comparison',
    'visualization', 'metrics', 'numbers', 'percentage'
  ],
  social: [
    'social media', 'instagram', 'twitter', 'facebook', 'post',
    'share', 'viral', 'engagement', 'story'
  ],
  slide: [
    'slide', 'presentation', 'deck', 'powerpoint', 'keynote',
    'pitch', 'deck', 'slideshow'
  ]
};

function extractKeywords(text: string): string[] {
  const lower = text.toLowerCase();
  const words = lower.split(/\s+/);
  const phrases = lower.match(/\b\w+\s+\w+\b/g) || [];
  return [...words, ...phrases];
}

function scoreScene(content: string, scene: SceneType): SceneScore {
  const keywords = extractKeywords(content);
  const sceneKeywords = SCENE_KEYWORDS[scene];
  
  let score = 0;
  const reasons: string[] = [];
  
  for (const keyword of sceneKeywords) {
    const count = keywords.filter(k => k.includes(keyword)).length;
    if (count > 0) {
      score += count;
      reasons.push(`Found "${keyword}" keyword`);
    }
  }
  
  // Normalize score (0-1 range)
  const normalizedScore = Math.min(score / 10, 1);
  
  let confidence: 'high' | 'medium' | 'low';
  if (normalizedScore > 0.7) confidence = 'high';
  else if (normalizedScore > 0.4) confidence = 'medium';
  else confidence = 'low';
  
  return {
    scene,
    score: normalizedScore,
    confidence,
    reasons
  };
}

function detectScene(content: string, metadata?: Record<string, any>): SceneScore[] {
  // Check explicit scene hint in metadata
  if (metadata?.scene) {
    const explicitScene = metadata.scene as SceneType;
    return [{
      scene: explicitScene,
      score: 1.0,
      confidence: 'high',
      reasons: ['Explicit scene specified in metadata']
    }];
  }
  
  // Score all scenes
  const scores: SceneScore[] = Object.keys(SCENE_KEYWORDS).map(scene =>
    scoreScene(content, scene as SceneType)
  );
  
  // Sort by score descending
  scores.sort((a, b) => b.score - a.score);
  
  return scores;
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error('Usage: detect-scene.ts <file-path>');
    process.exit(1);
  }
  
  const filePath = args[0];
  
  try {
    const content = await readFile(filePath, 'utf-8');
    
    // Try to extract frontmatter if markdown
    let metadata: Record<string, any> = {};
    if (extname(filePath) === '.md') {
      const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
      if (frontmatterMatch) {
        // Simple YAML parsing (basic)
        const yaml = frontmatterMatch[1];
        yaml.split('\n').forEach(line => {
          const match = line.match(/^(\w+):\s*(.+)$/);
          if (match) {
            metadata[match[1]] = match[2].trim();
          }
        });
      }
    }
    
    const results = detectScene(content, metadata);
    
    // Output as JSON for easy parsing
    console.log(JSON.stringify({
      primary: results[0],
      alternatives: results.slice(1, 3),
      all: results
    }, null, 2));
    
  } catch (error) {
    console.error(`Error reading file: ${error}`);
    process.exit(1);
  }
}

if (import.meta.main) {
  main();
}

export { detectScene, SceneType, SceneScore };

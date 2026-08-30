import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

export const KnowledgeGraph = ({ graphData, onSelectNode }) => {
  const svgRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) return;

    const width = containerRef.current?.clientWidth || 700;
    const height = 450;

    // Clear previous SVG
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height]);

    // Color scale for node types
    const colorMap = {
      Case: '#2563eb',       // Blue
      Evidence: '#10b981',   // Green
      Artifact: '#8b5cf6',   // Purple
      Device: '#f59e0b',     // Amber
      Event: '#06b6d4',      // Cyan
      Source: '#64748b',     // Slate
    };

    // Prepare links and nodes deep copies for D3 force simulation
    const nodes = graphData.nodes.map(d => ({ ...d }));
    const links = graphData.links.map(d => ({ ...d }));

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(90))
      .force('charge', d3.forceManyBody().strength(-250))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    // Render arrow markers for directed links
    svg.append('defs').append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('fill', '#94a3b8')
      .attr('d', 'M0,-5L10,0L0,5');

    // Draw Links
    const link = svg.append('g')
      .attr('stroke', '#cbd5e1')
      .attr('stroke-opacity', 0.8)
      .attr('stroke-width', 1.5)
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('marker-end', 'url(#arrow)');

    // Link Labels
    const linkLabel = svg.append('g')
      .selectAll('text')
      .data(links)
      .join('text')
      .text(d => d.type)
      .attr('font-size', '8px')
      .attr('font-weight', '600')
      .attr('fill', '#94a3b8')
      .attr('text-anchor', 'middle');

    // Draw Nodes
    const node = svg.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .style('cursor', 'pointer')
      .call(d3.drag()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
      )
      .on('click', (event, d) => {
        if (onSelectNode) onSelectNode(d);
      });

    node.append('circle')
      .attr('r', 16)
      .attr('fill', d => colorMap[d.type] || '#64748b')
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2)
      .attr('class', 'shadow-sm');

    node.append('text')
      .text(d => d.label)
      .attr('x', 20)
      .attr('y', 4)
      .attr('font-size', '10px')
      .attr('font-weight', '700')
      .attr('fill', '#1e293b');

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      linkLabel
        .attr('x', d => (d.source.x + d.target.x) / 2)
        .attr('y', d => (d.source.y + d.target.y) / 2 - 2);

      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    return () => simulation.stop();
  }, [graphData]);

  return (
    <div ref={containerRef} className="w-full bg-slate-900/5 rounded-xl border border-slate-200 overflow-hidden relative">
      <svg ref={svgRef} className="w-full h-[450px]"></svg>
    </div>
  );
};

export default KnowledgeGraph;

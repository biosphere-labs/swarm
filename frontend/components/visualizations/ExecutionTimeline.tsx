'use client';

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { TimelineEvent, STATUS_COLORS } from '@/types/visualization';

interface ExecutionTimelineProps {
  events: TimelineEvent[];
  width?: number;
  height?: number;
}

export function ExecutionTimeline({ events, width = 800, height = 400 }: ExecutionTimelineProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || events.length === 0) return;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 100 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    // Flatten events for timeline view
    const flatEvents = events.flatMap((event) => {
      const result = [event];
      if (event.children) {
        result.push(...event.children);
      }
      return result;
    });

    // Create time scale
    const minTime = d3.min(flatEvents, (d) => d.startTime.getTime()) || 0;
    const maxTime = d3.max(flatEvents, (d) => (d.endTime || new Date()).getTime()) || 0;

    const xScale = d3
      .scaleTime()
      .domain([new Date(minTime), new Date(maxTime)])
      .range([0, innerWidth]);

    // Create y scale for events
    const yScale = d3
      .scaleBand()
      .domain(flatEvents.map((d) => d.id))
      .range([0, innerHeight])
      .padding(0.2);

    // Add X axis
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale).ticks(5).tickFormat(d3.timeFormat('%H:%M:%S') as any))
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)');

    // Add Y axis
    g.append('g')
      .call(d3.axisLeft(yScale).tickFormat((d) => {
        const event = flatEvents.find((e) => e.id === d);
        return event ? event.name : '';
      }))
      .selectAll('text')
      .style('font-size', '12px');

    // Add bars for events
    g.selectAll('.bar')
      .data(flatEvents)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', (d) => xScale(d.startTime))
      .attr('y', (d) => yScale(d.id) || 0)
      .attr('width', (d) => {
        const endTime = d.endTime || new Date();
        return Math.max(2, xScale(endTime) - xScale(d.startTime));
      })
      .attr('height', yScale.bandwidth())
      .attr('fill', (d) => STATUS_COLORS[d.status])
      .attr('rx', 4)
      .style('cursor', 'pointer')
      .on('mouseover', function (event, d) {
        d3.select(this).attr('opacity', 0.7);

        // Show tooltip
        const tooltip = g.append('g').attr('class', 'tooltip');
        const duration = d.endTime
          ? (d.endTime.getTime() - d.startTime.getTime()) / 1000
          : 'In progress';

        tooltip
          .append('rect')
          .attr('x', xScale(d.startTime) + 5)
          .attr('y', (yScale(d.id) || 0) - 30)
          .attr('width', 150)
          .attr('height', 25)
          .attr('fill', 'white')
          .attr('stroke', '#ccc')
          .attr('rx', 4);

        tooltip
          .append('text')
          .attr('x', xScale(d.startTime) + 10)
          .attr('y', (yScale(d.id) || 0) - 10)
          .text(`Duration: ${duration}s`)
          .style('font-size', '12px');
      })
      .on('mouseout', function () {
        d3.select(this).attr('opacity', 1);
        g.selectAll('.tooltip').remove();
      });

    // Add grid lines
    g.append('g')
      .attr('class', 'grid')
      .attr('opacity', 0.1)
      .call(
        d3
          .axisLeft(yScale)
          .tickSize(-innerWidth)
          .tickFormat(() => '')
      );
  }, [events, width, height]);

  return (
    <div className="w-full bg-white rounded-lg border p-4">
      <h3 className="text-lg font-semibold mb-4">Execution Timeline</h3>
      <svg ref={svgRef} className="w-full" />
    </div>
  );
}

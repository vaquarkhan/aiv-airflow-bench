    // Only the execution bar should be rendered; scheduled and queued are too narrow.
    expect(screen.getAllByRole("link")).toHaveLength(1);
  });

  it("hatches a task-group aggregate bar so it does not read as a single long task", () => {
    const groupNode: GridTask = {
      depth: 0,
      id: "group_1",
      is_mapped: false,
      isGroup: true,
      label: "group_1",
    };
    const groupSegment: GanttDataItem = {
      queued_when: null,
      scheduled_when: null,
      state: "success",
      taskId: "group_1",
      tryNumber: undefined,
      x: [new Date("2024-03-14T10:00:00Z").getTime(), new Date("2024-03-14T10:05:00Z").getTime()],
      y: "group_1",
    };
    const leafSegment: GanttDataItem = {
      queued_when: null,
      scheduled_when: null,
      state: "success",
      taskId: "task_1",
      tryNumber: 1,
      x: [new Date("2024-03-14T10:00:00Z").getTime(), new Date("2024-03-14T10:05:00Z").getTime()],
      y: "task_1",
    };

    render(
      <GanttTimeline
        {...defaultProps}
        flatNodes={[groupNode, BASE_NODE]}
        ganttDataItems={[groupSegment, leafSegment]}
        rowSegments={[[groupSegment], [leafSegment]]}
        scrollContainerRef={makeScrollRef()}
      />,
      { wrapper: TestWrapper },
    );

    const bars = screen.getAllByRole("link");

    // Group aggregate bar carries the diagonal-stripe overlay.
    expect(bars[0]?.querySelector('[style*="repeating-linear-gradient"]')).not.toBeNull();
    // Regular task bar does not.
    expect(bars[1]?.querySelector('[style*="repeating-linear-gradient"]')).toBeNull();
  });
});

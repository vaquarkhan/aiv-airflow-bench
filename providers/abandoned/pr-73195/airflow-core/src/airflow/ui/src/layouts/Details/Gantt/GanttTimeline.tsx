                              justifyContent="center"
                              minH={0}
                              p={0}
                              // Aggregate task-group bars are the envelope of their children's
                              // runtime, not a real running task. Overlay a diagonal stripe so
                              // they read as an aggregate at a glance and don't get mistaken for
                              // a single long-running task.
                              style={
                                node.isGroup === true
                                  ? {
                                      backgroundImage:
                                        "repeating-linear-gradient(45deg, rgba(255,255,255,0.4) 0px, rgba(255,255,255,0.4) 3px, transparent 3px, transparent 6px)",
                                    }
                                  : undefined
                              }
                              variant="solid"
                              w="100%"
                            >

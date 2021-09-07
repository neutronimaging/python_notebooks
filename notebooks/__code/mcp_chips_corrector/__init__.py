from qtpy.QtGui import QColor

CHIP_CORRECTION = {'low': {1: {'xoffset': 0,
                               'yoffset': 0},
                           2: {'xoffset': 2,
                               'yoffset': 0},
                           3: {'xoffset': 0,
                               'yoffset': 3},
                           4: {'xoffset': 2,
                               'yoffset': 3},
                           },
                   'high': {1: {'xoffset': 0,
                                'yoffset': 0},
                            2: {'xoffset': 16,
                                'yoffset': 0},
                            3: {'xoffset': 0,
                                'yoffset': 16},
                            4: {'xoffset': 8,
                                'yoffset': 16},
                            },
                   }
CHIP_GAP = {'low': {'xoffset': 2,
                    'yoffset': 3,
                    },
            'high': {'xoffset': 8,
                     'yoffset': 16,
                     }
            }

NBR_OF_EDGES_PIXEL_TO_NOT_USE = 1

COLOR_CONTOUR = QColor(255, 0, 0, 255)
PROFILE_ROI = QColor(255, 255, 255, 255)
INTER_CHIPS = QColor(0, 255, 0, 255)

MCP_LOW_MODE = 512  # pixel

LOG_FILENAME = ".mcp_chips_corrector.log"

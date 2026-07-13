(define (problem smart-battery-warehouse-current-state)
  (:domain smart-battery-warehouse)

  (:objects
    battery-zone manager-zone - zone
    manager-dashboard - dashboard
  )

  (:init
    (light-off manager-zone)
    (needs-dashboard-update manager-dashboard)
    (needs-green-light manager-zone)
    (needs-shutter-open manager-zone)
    (needs-battery-maintenance battery-zone)
  )

  (:goal
    (and
      (dashboard-updated manager-dashboard)
      (fan-off battery-zone)
      (alarm-off battery-zone)
      (green-light-on manager-zone)
      (shutter-open manager-zone)
      (battery-maintenance-requested battery-zone)
    )
  )
)

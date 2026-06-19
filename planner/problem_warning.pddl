(define (problem battery-warehouse-warning)
  (:domain battery-warehouse)

  (:objects
    zone1 - zone
    fan1 - fan
    alarm1 - alarm
    led1 - light
    shutter1 - shutter
    battery1 - battery
  )

  (:init
    ;; warning context
    (temperature-high zone1)
    (battery-warning battery1)

    ;; no emergency occupancy action needed
    ;; occupancy is not included, so request-evacuation is not applicable

    ;; actuator initial states
    (fan-off fan1)
    (alarm-off alarm1)
    (warning-light-off led1)
    (shutter-open shutter1)
  )

  (:goal
    (and
      (ventilation-active zone1)
      (warning-light-on led1)
      (manager-notified zone1)
    )
  )
)
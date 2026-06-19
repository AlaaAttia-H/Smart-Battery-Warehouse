(define (domain battery-warehouse)
  (:requirements :strips :typing)

  (:types
    zone
    fan
    alarm
    light
    shutter
    battery
  )

  (:predicates
    ;; environment/context states
    (temperature-high ?z - zone)
    (temperature-critical ?z - zone)
    (co2-high ?z - zone)
    (co2-critical ?z - zone)
    (occupied ?z - zone)
    (battery-warning ?b - battery)
    (battery-critical ?b - battery)

    ;; actuator states
    (fan-off ?f - fan)
    (fan-on ?f - fan)

    (alarm-off ?a - alarm)
    (alarm-on ?a - alarm)

    (warning-light-off ?l - light)
    (warning-light-on ?l - light)

    (shutter-open ?s - shutter)
    (shutter-closed ?s - shutter)

    ;; achieved safety states
    (ventilation-active ?z - zone)
    (manager-notified ?z - zone)
    (evacuation-requested ?z - zone)
    (zone-isolated ?z - zone)
  )

  (:action start-fan
    :parameters (?f - fan ?z - zone)
    :precondition (fan-off ?f)
    :effect (and
      (fan-on ?f)
      (ventilation-active ?z)
      (not (fan-off ?f))
    )
  )

  (:action activate-alarm
    :parameters (?a - alarm)
    :precondition (alarm-off ?a)
    :effect (and
      (alarm-on ?a)
      (not (alarm-off ?a))
    )
  )

  (:action turn-on-warning-light
    :parameters (?l - light)
    :precondition (warning-light-off ?l)
    :effect (and
      (warning-light-on ?l)
      (not (warning-light-off ?l))
    )
  )

  (:action notify-manager
    :parameters (?z - zone)
    :precondition (and)
    :effect (manager-notified ?z)
  )

  (:action request-evacuation
    :parameters (?z - zone)
    :precondition (occupied ?z)
    :effect (evacuation-requested ?z)
  )

  (:action close-shutter
    :parameters (?s - shutter ?z - zone)
    :precondition (shutter-open ?s)
    :effect (and
      (shutter-closed ?s)
      (zone-isolated ?z)
      (not (shutter-open ?s))
    )
  )
)
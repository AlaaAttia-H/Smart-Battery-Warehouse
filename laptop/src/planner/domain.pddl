(define (domain smart-battery-warehouse)
  (:requirements :strips :typing)

  (:types
    zone dashboard
  )

  (:predicates
    ;; Context needs
    (needs-ventilation ?z - zone)
    (needs-alarm ?z - zone)
    (needs-red-light ?z - zone)
    (needs-orange-light ?z - zone)
    (needs-green-light ?z - zone)
    (needs-shutter-open ?z - zone)
    (needs-shutter-closed ?z - zone)
    (needs-manager-notification ?z - zone)
    (needs-dashboard-update ?d - dashboard)
    (needs-evacuation ?z - zone)

    ;; Battery condition needs
    (needs-battery-warning ?z - zone)
    (needs-battery-maintenance ?z - zone)

    ;; Actuator / system states
    (fan-on ?z - zone)
    (fan-off ?z - zone)

    (alarm-on ?z - zone)
    (alarm-off ?z - zone)

    (red-light-on ?z - zone)
    (orange-light-on ?z - zone)
    (green-light-on ?z - zone)
    (light-off ?z - zone)

    (shutter-open ?z - zone)
    (shutter-closed ?z - zone)

    (manager-notified ?z - zone)
    (dashboard-updated ?d - dashboard)
    (evacuation-requested ?z - zone)

    (battery-warning-sent ?z - zone)
    (battery-maintenance-requested ?z - zone)
  )

  (:action start-fan
    :parameters (?z - zone)
    :precondition (needs-ventilation ?z)
    :effect (and
      (fan-on ?z)
      (not (fan-off ?z))
    )
  )

  (:action stop-fan
    :parameters (?z - zone)
    :precondition (and)
    :effect (and
      (fan-off ?z)
      (not (fan-on ?z))
    )
  )

  (:action activate-alarm
    :parameters (?z - zone)
    :precondition (needs-alarm ?z)
    :effect (and
      (alarm-on ?z)
      (not (alarm-off ?z))
    )
  )

  (:action deactivate-alarm
    :parameters (?z - zone)
    :precondition (and)
    :effect (and
      (alarm-off ?z)
      (not (alarm-on ?z))
    )
  )

  (:action set-red-light
    :parameters (?z - zone)
    :precondition (needs-red-light ?z)
    :effect (and
      (red-light-on ?z)
      (not (orange-light-on ?z))
      (not (green-light-on ?z))
      (not (light-off ?z))
    )
  )

  (:action set-orange-light
    :parameters (?z - zone)
    :precondition (needs-orange-light ?z)
    :effect (and
      (orange-light-on ?z)
      (not (red-light-on ?z))
      (not (green-light-on ?z))
      (not (light-off ?z))
    )
  )

  (:action set-green-light
    :parameters (?z - zone)
    :precondition (needs-green-light ?z)
    :effect (and
      (green-light-on ?z)
      (not (red-light-on ?z))
      (not (orange-light-on ?z))
      (not (light-off ?z))
    )
  )

  (:action open-shutter
    :parameters (?z - zone)
    :precondition (needs-shutter-open ?z)
    :effect (and
      (shutter-open ?z)
      (not (shutter-closed ?z))
    )
  )

  (:action close-shutter
    :parameters (?z - zone)
    :precondition (needs-shutter-closed ?z)
    :effect (and
      (shutter-closed ?z)
      (not (shutter-open ?z))
    )
  )

  (:action notify-manager
    :parameters (?z - zone)
    :precondition (needs-manager-notification ?z)
    :effect (manager-notified ?z)
  )

  (:action update-dashboard
    :parameters (?d - dashboard)
    :precondition (needs-dashboard-update ?d)
    :effect (dashboard-updated ?d)
  )

  (:action request-evacuation
    :parameters (?z - zone)
    :precondition (needs-evacuation ?z)
    :effect (evacuation-requested ?z)
  )

  (:action send-battery-warning
    :parameters (?z - zone)
    :precondition (needs-battery-warning ?z)
    :effect (battery-warning-sent ?z)
  )

  (:action request-battery-maintenance
    :parameters (?z - zone)
    :precondition (needs-battery-maintenance ?z)
    :effect (battery-maintenance-requested ?z)
  )
)
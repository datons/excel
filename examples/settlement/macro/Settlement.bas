Attribute VB_Name = "Settlement"
Option Explicit

' Settles the energy of one installation per day from the Medidas, Precios and Parametros sheets, and writes the result to Liquidacion.
' Billable energy per hour: measured kWh / 1000 * (1 + losses).
' Amount per hour: Round(MWh * (price + toll), 2), with VBA rounding, before adding up the day.
' An hour without a measure takes the average of the measured hours of that day; a day without any measure settles to zero and is flagged.
' Keep this file ASCII: the VBA editor reads it in the local code page (MacRoman on Mac, cp1252 on Windows), so any accent would be garbled.

Public Sub Settle()
    Dim measures As Worksheet, prices As Worksheet, params As Worksheet, result As Worksheet
    Set measures = ThisWorkbook.Worksheets("Medidas")
    Set prices = ThisWorkbook.Worksheets("Precios")
    Set params = ThisWorkbook.Worksheets("Parametros")
    Set result = ThisWorkbook.Worksheets("Liquidacion")

    Dim losses As Double, toll As Double
    losses = params.Range("B2").Value
    toll = params.Range("B3").Value

    result.Range("A2:F1000").ClearContents

    Dim lastRow As Long, r As Long, dayStart As Long, outRow As Long, grandTotal As Double
    lastRow = measures.Cells(measures.Rows.Count, 1).End(xlUp).Row
    dayStart = 2
    outRow = 2

    For r = 3 To lastRow + 1
        If r > lastRow Then
            grandTotal = grandTotal + SettleDay(measures, prices, result, dayStart, r - 1, outRow, losses, toll)
            outRow = outRow + 1
        ElseIf measures.Cells(r, 1).Value <> measures.Cells(dayStart, 1).Value Then
            grandTotal = grandTotal + SettleDay(measures, prices, result, dayStart, r - 1, outRow, losses, toll)
            outRow = outRow + 1
            dayStart = r
        End If
    Next r

    result.Cells(outRow, 1).Value = "Total"
    result.Cells(outRow, 6).Value = grandTotal
End Sub

Private Function SettleDay(measures As Worksheet, prices As Worksheet, result As Worksheet, firstRow As Long, lastRow As Long, outRow As Long, losses As Double, toll As Double) As Double
    Dim r As Long, hoursInDay As Long, measured As Long, estimated As Long, sumKwh As Double
    For r = firstRow To lastRow
        hoursInDay = hoursInDay + 1
        If Not IsEmpty(measures.Cells(r, 3).Value) Then
            measured = measured + 1
            sumKwh = sumKwh + measures.Cells(r, 3).Value
        End If
    Next r

    Dim average As Double
    If measured > 0 Then average = sumKwh / measured

    Dim kwh As Double, mwh As Double, energy As Double, amount As Double, total As Double
    For r = firstRow To lastRow
        If IsEmpty(measures.Cells(r, 3).Value) Then
            kwh = average
            estimated = estimated + 1
        Else
            kwh = measures.Cells(r, 3).Value
        End If
        mwh = kwh / 1000 * (1 + losses)
        energy = energy + mwh
        amount = Round(mwh * (PriceAt(prices, measures.Cells(r, 1).Value, measures.Cells(r, 2).Value) + toll), 2)
        total = total + amount
    Next r

    result.Cells(outRow, 1).Value = measures.Cells(firstRow, 1).Value
    result.Cells(outRow, 2).Value = hoursInDay
    result.Cells(outRow, 3).Value = estimated
    result.Cells(outRow, 4).Value = energy
    If measured = 0 Then result.Cells(outRow, 5).Value = "sin medidas"
    result.Cells(outRow, 6).Value = total
    SettleDay = total
End Function

' Price of a date and hour, searched row by row in the Precios sheet. Returns 0 when it is not there.
Private Function PriceAt(prices As Worksheet, dateValue As Variant, hourValue As Variant) As Double
    Dim r As Long
    For r = 2 To prices.Cells(prices.Rows.Count, 1).End(xlUp).Row
        If prices.Cells(r, 1).Value = dateValue And prices.Cells(r, 2).Value = hourValue Then
            PriceAt = prices.Cells(r, 3).Value
            Exit Function
        End If
    Next r
    PriceAt = 0
End Function

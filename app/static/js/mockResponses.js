const mockResponses = {
  "which properties are non-compliant": `
    <strong>7 non-compliant properties</strong> found across the portfolio:<br><br>

    <table class="govuk-table">
      <thead class="govuk-table__head">
        <tr class="govuk-table__row">
          <th class="govuk-table__header">Address</th>
          <th class="govuk-table__header">Issue</th>
        </tr>
      </thead>

      <tbody class="govuk-table__body">
        <tr class="govuk-table__row">
          <td class="govuk-table__cell">14 Birchwood Ave</td>
          <td class="govuk-table__cell">Gas safety certificate expired (547 days)</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">8 Maple Court</td>
          <td class="govuk-table__cell">Fire alarm inspection overdue (426 days)</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">19 Primrose Way</td>
          <td class="govuk-table__cell">Gas safety certificate expired (517 days)</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">+ 4 more</td>
          <td class="govuk-table__cell">View full compliance list</td>
        </tr>
      </tbody>
    </table>
  `,

  "show overdue inspections": `
    <strong>14 properties</strong> have not been inspected in over 12 months.<br><br>

    <table class="govuk-table">
      <thead class="govuk-table__head">
        <tr class="govuk-table__row">
          <th class="govuk-table__header">Address</th>
          <th class="govuk-table__header">Days overdue</th>
        </tr>
      </thead>

      <tbody class="govuk-table__body">
        <tr class="govuk-table__row">
          <td class="govuk-table__cell">4 Thornton Gardens</td>
          <td class="govuk-table__cell">578 days</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">14 Birchwood Ave</td>
          <td class="govuk-table__cell">547 days</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">19 Primrose Way</td>
          <td class="govuk-table__cell">517 days</td>
        </tr>
      </tbody>
    </table>
  `,

  "find all boiler repair records": `
    Found <strong>3 boiler-related repair records</strong> across database and documents:<br><br>

    <table class="govuk-table">
      <thead class="govuk-table__head">
        <tr class="govuk-table__row">
          <th class="govuk-table__header">Property</th>
          <th class="govuk-table__header">Date</th>
          <th class="govuk-table__header">Contractor</th>
          <th class="govuk-table__header">Cost</th>
        </tr>
      </thead>

      <tbody class="govuk-table__body">
        <tr class="govuk-table__row">
          <td class="govuk-table__cell">14 Birchwood Ave</td>
          <td class="govuk-table__cell">Mar 2024</td>
          <td class="govuk-table__cell">Patel Plumbing Ltd</td>
          <td class="govuk-table__cell">£1,840</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">8 Maple Court</td>
          <td class="govuk-table__cell">Jan 2024</td>
          <td class="govuk-table__cell">CityGas Ltd</td>
          <td class="govuk-table__cell">£180</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">22 Heather Close</td>
          <td class="govuk-table__cell">Oct 2023</td>
          <td class="govuk-table__cell">Patel Plumbing Ltd</td>
          <td class="govuk-table__cell">£420</td>
        </tr>
      </tbody>
    </table>

    <br>
    Also matched document: <strong>boiler_repair_report_2024-03.txt</strong> (score 0.94)
  `,

  "list open foi requests": `
    <strong>4 active STAIRS / FOI requests</strong> currently open:<br><br>

    <table class="govuk-table">
      <thead class="govuk-table__head">
        <tr class="govuk-table__row">
          <th class="govuk-table__header">Reference</th>
          <th class="govuk-table__header">Due date</th>
          <th class="govuk-table__header">Days remaining</th>
        </tr>
      </thead>

      <tbody class="govuk-table__body">
        <tr class="govuk-table__row">
          <td class="govuk-table__cell">FOI-2025-0041</td>
          <td class="govuk-table__cell">8 May 2025</td>
          <td class="govuk-table__cell app-deadline--urgent">3 days</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">FOI-2025-0038</td>
          <td class="govuk-table__cell">13 May 2025</td>
          <td class="govuk-table__cell">8 days</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">FOI-2025-0035</td>
          <td class="govuk-table__cell">20 May 2025</td>
          <td class="govuk-table__cell">15 days</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">FOI-2025-0031</td>
          <td class="govuk-table__cell">26 May 2025</td>
          <td class="govuk-table__cell">21 days</td>
        </tr>
      </tbody>
    </table>
  `,

  "properties with damp issues": `
    Found <strong>2 properties</strong> with damp or mould records, plus 1 document match:<br><br>

    <table class="govuk-table">
      <thead class="govuk-table__head">
        <tr class="govuk-table__row">
          <th class="govuk-table__header">Property</th>
          <th class="govuk-table__header">Details</th>
        </tr>
      </thead>

      <tbody class="govuk-table__body">
        <tr class="govuk-table__row">
          <td class="govuk-table__cell">14 Birchwood Ave</td>
          <td class="govuk-table__cell">Damp treatment Aug 2023 — ProDamp Solutions — resolved</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">2 Ash Lane</td>
          <td class="govuk-table__cell">Assessment overdue — no treatment on record</td>
        </tr>

        <tr class="govuk-table__row">
          <td class="govuk-table__cell">Document match</td>
          <td class="govuk-table__cell">damp_mould_risk_note.txt — relevance score 0.91</td>
        </tr>
      </tbody>
    </table>
  `
};
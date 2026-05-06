const nonCompliantTable = `
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
    </tbody>
  </table>
`;

const overdueInspectionsTable = `
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
`;

const boilerRepairTable = `
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
`;

const foiRequestsTable = `
  <table class="govuk-table">
    <thead class="govuk-table__head">
      <tr class="govuk-table__row">
        <th class="govuk-table__header">Reference</th>
        <th class="govuk-table__header">Due date</th>
        <th class="govuk-table__header">Days remaining</th>
    </tr>
    </thead>

    <tbody class="govuk-table__body">
      <tr class="govuk-table__row"><td class="govuk-table__cell">FOI-2025-0041</td><td class="govuk-table__cell">8 May 2025</td><td class="govuk-table__cell">3 days</td></tr>
      <tr class="govuk-table__row"><td class="govuk-table__cell">FOI-2025-0038</td><td class="govuk-table__cell">13 May 2025</td><td class="govuk-table__cell">8 days</td></tr>
      <tr class="govuk-table__row"><td class="govuk-table__cell">FOI-2025-0035</td><td class="govuk-table__cell">20 May 2025</td><td class="govuk-table__cell">15 days</td> </tr>
      <tr class="govuk-table__row"><td class="govuk-table__cell">FOI-2025-0031</td><td class="govuk-table__cell">26 May 2025</td><td class="govuk-table__cell">21 days</td></tr>
    </tbody>
    </tbody>
  </table>
`;

const dampIssuesTable = `
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
        <td class="govuk-table__cell">Damp treatment Aug 2023 — resolved</td>
      </tr>

      <tr class="govuk-table__row">
        <td class="govuk-table__cell">2 Ash Lane</td>
        <td class="govuk-table__cell">Assessment overdue — no treatment on record</td>
      </tr>
    </tbody>
  </table>
`;

const mockResponses = {

  "which properties are non-compliant": `
    <strong>3 non-compliant properties</strong> found.<br><br>

    <button type="button"
            class="govuk-button"
            onclick="openResultsModal('Non-compliant properties', nonCompliantTable)">
      Expand results
    </button>
  `,

  "show overdue inspections": `
    <strong>3 properties</strong> have overdue inspections.<br><br>

    <button type="button"
            class="govuk-button"
            onclick="openResultsModal('Overdue inspections', overdueInspectionsTable)">
      Expand results
    </button>
  `,

  "find all boiler repair records": `
    <strong>3 boiler repair records</strong> found.<br><br>

    <button type="button"
            class="govuk-button"
            onclick="openResultsModal('Boiler repair records', boilerRepairTable)">
      Expand results
    </button>
  `,

  "list open foi requests": `
    <strong>4 active FOI requests</strong> found.<br><br>

    <button type="button"
            class="govuk-button"
            onclick="openResultsModal('Open FOI requests', foiRequestsTable)">
      Expand results
    </button>
  `,

  "properties with damp issues": `
    <strong>2 properties</strong> with damp issues found.<br><br>

    <button type="button"
            class="govuk-button"
            onclick="openResultsModal('Damp and mould issues', dampIssuesTable)">
      Expand results
    </button>
  `
};
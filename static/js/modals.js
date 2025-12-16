/**
 * CPO Modal Helper Functions
 * Provides Bootstrap/AdminLTE styled modals instead of alert() and confirm()
 */

// Show success modal
function showSuccess(message, callback) {
    const modalHtml = `
        <div class="modal fade" id="successModal" tabindex="-1" role="dialog">
            <div class="modal-dialog modal-dialog-centered" role="document">
                <div class="modal-content">
                    <div class="modal-header bg-success">
                        <h5 class="modal-title text-white">
                            <i class="fas fa-check-circle"></i> Succes
                        </h5>
                        <button type="button" class="close text-white" data-dismiss="modal">
                            <span>&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-success" data-dismiss="modal">OK</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    $('#successModal').remove();

    // Add and show modal
    $('body').append(modalHtml);
    $('#successModal').modal('show');

    // Cleanup and callback
    $('#successModal').on('hidden.bs.modal', function() {
        $(this).remove();
        if (callback) callback();
    });
}

// Show error modal
function showError(message) {
    const modalHtml = `
        <div class="modal fade" id="errorModal" tabindex="-1" role="dialog">
            <div class="modal-dialog modal-dialog-centered" role="document">
                <div class="modal-content">
                    <div class="modal-header bg-danger">
                        <h5 class="modal-title text-white">
                            <i class="fas fa-exclamation-circle"></i> Eroare
                        </h5>
                        <button type="button" class="close text-white" data-dismiss="modal">
                            <span>&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-danger" data-dismiss="modal">OK</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    $('#errorModal').remove();

    // Add and show modal
    $('body').append(modalHtml);
    $('#errorModal').modal('show');

    // Cleanup
    $('#errorModal').on('hidden.bs.modal', function() {
        $(this).remove();
    });
}

// Show warning modal
function showWarning(message) {
    const modalHtml = `
        <div class="modal fade" id="warningModal" tabindex="-1" role="dialog">
            <div class="modal-dialog modal-dialog-centered" role="document">
                <div class="modal-content">
                    <div class="modal-header bg-warning">
                        <h5 class="modal-title text-dark">
                            <i class="fas fa-exclamation-triangle"></i> Atenție
                        </h5>
                        <button type="button" class="close" data-dismiss="modal">
                            <span>&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-warning" data-dismiss="modal">OK</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    $('#warningModal').remove();

    // Add and show modal
    $('body').append(modalHtml);
    $('#warningModal').modal('show');

    // Cleanup
    $('#warningModal').on('hidden.bs.modal', function() {
        $(this).remove();
    });
}

// Show confirmation modal
function showConfirm(message, onConfirm, onCancel) {
    const modalHtml = `
        <div class="modal fade" id="confirmModal" tabindex="-1" role="dialog">
            <div class="modal-dialog modal-dialog-centered" role="document">
                <div class="modal-content">
                    <div class="modal-header" style="background: #171E42;">
                        <h5 class="modal-title text-white">
                            <i class="fas fa-question-circle"></i> Confirmare
                        </h5>
                        <button type="button" class="close text-white" data-dismiss="modal">
                            <span>&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal" id="confirmCancel">
                            <i class="fas fa-times"></i> Anulează
                        </button>
                        <button type="button" class="btn btn-success" id="confirmOk">
                            <i class="fas fa-check"></i> Confirmă
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    $('#confirmModal').remove();

    // Add and show modal
    $('body').append(modalHtml);
    $('#confirmModal').modal('show');

    // Handle confirm
    $('#confirmOk').on('click', function() {
        $('#confirmModal').modal('hide');
        if (onConfirm) onConfirm();
    });

    // Handle cancel
    $('#confirmCancel').on('click', function() {
        if (onCancel) onCancel();
    });

    // Cleanup
    $('#confirmModal').on('hidden.bs.modal', function() {
        $(this).remove();
    });
}

// Show info modal
function showInfo(message) {
    const modalHtml = `
        <div class="modal fade" id="infoModal" tabindex="-1" role="dialog">
            <div class="modal-dialog modal-dialog-centered" role="document">
                <div class="modal-content">
                    <div class="modal-header bg-info">
                        <h5 class="modal-title text-white">
                            <i class="fas fa-info-circle"></i> Informație
                        </h5>
                        <button type="button" class="close text-white" data-dismiss="modal">
                            <span>&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-info" data-dismiss="modal">OK</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    $('#infoModal').remove();

    // Add and show modal
    $('body').append(modalHtml);
    $('#infoModal').modal('show');

    // Cleanup
    $('#infoModal').on('hidden.bs.modal', function() {
        $(this).remove();
    });
}
